"""
Legal AI Supervisor — api.py
FastAPI orchestration layer.

Endpoints:
  POST /agents/research        → run research agent
  POST /agents/drafting        → run drafting agent
  POST /agents/review          → run review agent
  POST /agents/risk_analysis   → run risk analysis agent
  POST /supervisor/run         → orchestrate all agents, loop, synthesise, escalate
  GET  /audit                  → full audit log
  GET  /health                 → sanity check
"""

import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from models import AgentRequest, AgentResult, SupervisorRequest, SupervisorResponse, SupervisorDecision
from agents import _call_agent, _extract_json, _supervisor_check, AUDIT_LOG, log_event, route_matter, _direct_llm_call
from store import (
    create_matter, get_matter, get_all_matters, update_matter,
    add_action, get_team_summary, TEAM
)

import json

app = FastAPI(
    title="Legal AI Supervisor",
    description="Supervised multi-agent system for legal work",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helper: call one agent and return a typed AgentResult
# ---------------------------------------------------------------------------
def _run_agent(agent_name: str, req: AgentRequest) -> AgentResult:
    raw, reasoning = _call_agent(agent_name, req.task, req.context, req.feedback)

    try:
        parsed = json.loads(_extract_json(raw))
    except json.JSONDecodeError:
        log_event("supervisor", "parse_error", {"agent": agent_name, "raw": raw[:200]})
        parsed = {
            "output": raw,
            "confidence": 30,
            "risk": 80,
            "citations": [],
            "flags": ["PARSE ERROR — response was not valid JSON; human review required"],
        }

    return AgentResult(
        agent=agent_name,
        attempt=req.attempt,
        output=parsed.get("output", ""),
        confidence=int(parsed.get("confidence", 0)),
        risk=int(parsed.get("risk", 100)),
        citations=parsed.get("citations", []),
        flags=parsed.get("flags", []),
        reasoning=reasoning,
    )


# ---------------------------------------------------------------------------
# Individual agent endpoints (callable independently or by the supervisor)
# ---------------------------------------------------------------------------

@app.post("/agents/research", response_model=AgentResult)
def agent_research(req: AgentRequest):
    """Legal research agent: case law, statutes, principles."""
    return _run_agent("research", req)


@app.post("/agents/drafting", response_model=AgentResult)
def agent_drafting(req: AgentRequest):
    """Legal drafting agent: clauses, contracts, letters."""
    return _run_agent("drafting", req)


@app.post("/agents/review", response_model=AgentResult)
def agent_review(req: AgentRequest):
    """Legal review agent: errors, gaps, compliance issues."""
    return _run_agent("review", req)


@app.post("/agents/risk_analysis", response_model=AgentResult)
def agent_risk_analysis(req: AgentRequest):
    """Legal risk analysis agent: risks with legal basis, classified HIGH/MEDIUM/LOW."""
    return _run_agent("risk_analysis", req)


# ---------------------------------------------------------------------------
# Supervisor endpoint — orchestrates all agents
# ---------------------------------------------------------------------------

@app.post("/supervisor/run", response_model=SupervisorResponse)
def supervisor_run(req: SupervisorRequest):
    """
    Supervisor orchestration loop:
    1. Run all requested agents in parallel (via threads — NVIDIA API is blocking).
    2. Supervisor evaluates each agent result against thresholds.
    3. If any agent fails, retry only failing agents with targeted feedback.
    4. After max_iterations, escalate any still-failing agents to human.
    5. Synthesise a cross-agent summary.
    """

    attempt_history = []
    # Track the best result per agent (last passing, or last attempt if never passed)
    best_results: dict[str, AgentResult] = {}
    # Track which agents still need more work
    pending_agents = list(req.agents)
    # Track feedback per agent from the supervisor
    agent_feedback: dict[str, str] = {a: "" for a in req.agents}

    for iteration in range(1, req.max_iterations + 1):
        if not pending_agents:
            break

        log_event("supervisor", "iteration_start", {
            "iteration": iteration,
            "pending_agents": pending_agents,
        })

        # Run pending agents in parallel using asyncio + threads
        agent_requests = {
            agent: AgentRequest(
                task=req.task,
                context=req.context,
                feedback=agent_feedback.get(agent, ""),
                attempt=iteration,
            )
            for agent in pending_agents
        }

        # Thread pool execution (NVIDIA SDK is sync/blocking)
        loop = asyncio.new_event_loop()
        async def run_all():
            tasks = [
                asyncio.to_thread(_run_agent, agent, agent_req)
                for agent, agent_req in agent_requests.items()
            ]
            return await asyncio.gather(*tasks)
        results_list = loop.run_until_complete(run_all())
        loop.close()

        # Map back to agent names
        results: dict[str, AgentResult] = {
            agent: result
            for agent, result in zip(pending_agents, results_list)
        }

        # Supervisor evaluates each result
        decisions: list[SupervisorDecision] = []
        still_failing = []

        for agent, result in results.items():
            passed, issues = _supervisor_check(
                {"confidence": result.confidence, "risk": result.risk, "flags": result.flags},
                req.confidence_threshold,
                req.risk_threshold,
            )
            result.passed = passed
            result.issues = issues
            best_results[agent] = result  # always keep the latest

            decision = SupervisorDecision(
                agent=agent,
                passed=passed,
                issues=issues,
                confidence=result.confidence,
                risk=result.risk,
            )
            decisions.append(decision)

            log_event("supervisor", "evaluate", {
                "iteration": iteration,
                "agent": agent,
                "confidence": result.confidence,
                "risk": result.risk,
                "passed": passed,
                "issues": issues,
            })

            if not passed:
                still_failing.append(agent)
                # Build targeted feedback for the next attempt
                agent_feedback[agent] = (
                    f"Issues from attempt {iteration}: {'; '.join(issues)}. "
                    "Improve grounding, add more specific citations, and address each issue directly."
                )

        attempt_history.append({
            "iteration": iteration,
            "decisions": [d.model_dump() for d in decisions],
        })

        pending_agents = still_failing

        if not still_failing:
            log_event("supervisor", "all_passed", {"iteration": iteration})
            break

    # Determine overall status
    failed_agents = [a for a, r in best_results.items() if not r.passed]
    status = "accepted" if not failed_agents else "needs_human_review"
    escalation_reason = None
    if failed_agents:
        reasons = []
        for a in failed_agents:
            reasons.append(f"{a}: {'; '.join(best_results[a].issues)}")
        escalation_reason = " | ".join(reasons)
        log_event("supervisor", "escalate", {"failed_agents": failed_agents, "reason": escalation_reason})

    # Cross-agent synthesis
    synthesis = _synthesise(req.task, best_results, status)

    # Aggregate metrics
    confidences = [r.confidence for r in best_results.values()]
    risks = [r.risk for r in best_results.values()]
    all_flags = [f for r in best_results.values() for f in r.flags]
    high_flags = [f for f in all_flags if str(f).upper().startswith("HIGH")]

    return SupervisorResponse(
        status=status,
        total_attempts=min(req.max_iterations, len(attempt_history)),
        escalation_reason=escalation_reason,
        agent_results={a: r for a, r in best_results.items()},
        synthesis=synthesis,
        overall_confidence=int(sum(confidences) / len(confidences)) if confidences else 0,
        overall_risk=max(risks) if risks else 100,
        high_flag_count=len(high_flags),
        audit_log=AUDIT_LOG.copy(),
        attempt_history=attempt_history,
    )


# ---------------------------------------------------------------------------
# Synthesis — supervisor combines all agent outputs into one summary
# ---------------------------------------------------------------------------
def _synthesise(task: str, results: dict[str, AgentResult], status: str) -> str:
    if not results:
        return "No agent results to synthesise."

    parts = [f"Supervisor synthesis for: {task}\n"]
    parts.append(f"Overall status: {status.upper()}\n")

    for agent, result in results.items():
        label = agent.replace("_", " ").title()
        passed_str = "✅ PASSED" if result.passed else "🚨 ESCALATED"
        parts.append(
            f"[{label} — {passed_str} | Confidence: {result.confidence}% | Risk: {result.risk}%]\n"
            f"{result.output[:400]}{'...' if len(result.output) > 400 else ''}\n"
        )

    all_high = [f for r in results.values() for f in r.flags if str(f).upper().startswith("HIGH")]
    if all_high:
        parts.append(f"\nCritical flags requiring lawyer attention ({len(all_high)}):")
        for f in all_high:
            parts.append(f"  • {f}")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Utility endpoints
# ---------------------------------------------------------------------------

@app.get("/audit")
def get_audit():
    return {"entries": AUDIT_LOG, "count": len(AUDIT_LOG)}


@app.get("/health")
def health():
    return {"status": "ok", "audit_entries": len(AUDIT_LOG)}


# ---------------------------------------------------------------------------
# Matter management endpoints
# ---------------------------------------------------------------------------

class SubmitMatterRequest(BaseModel):
    client: str
    instructions: str
    partner_id: str
    matter_type: Optional[str] = "Commercial Contract Review"


class SubmitDraftRequest(BaseModel):
    matter_id: str
    junior_id: str
    draft: str


class SeniorDecisionRequest(BaseModel):
    matter_id: str
    senior_id: str
    decision: str          # "accepted" | "rejected"
    notes: Optional[str] = ""


class GenerateDraftRequest(BaseModel):
    matter_id: str
    junior_id: str


class AutonomousRequest(BaseModel):
    matter_id: str
    junior_id: str      # who triggered it (for audit)


@app.post("/matters/submit")
def submit_matter(req: SubmitMatterRequest):
    """
    Partner submits client instructions.
    AI Router reads team workload and assigns to the right junior + senior.
    """
    # Create matter
    matter = create_matter(req.client, req.instructions, req.partner_id, req.matter_type)

    # AI Router decides who gets it
    team_summary = get_team_summary()
    routing = route_matter(req.instructions, req.client, team_summary)

    # Update matter with routing decision
    update_matter(
        matter["id"],
        status="assigned",
        assigned_to=routing["junior_id"],
        senior_id=routing["senior_id"],
        matter_type=routing.get("matter_type", req.matter_type),
        routing=routing,
    )
    add_action(
        matter["id"],
        actor="router_ai",
        actor_type="ai",
        role="router_ai",
        action="assigned",
        detail=f"Assigned to {routing['junior_name']} — {routing['reasoning']}. Senior supervisor: {routing['senior_name']}.",
    )

    return {
        "matter_id": matter["id"],
        "routing": routing,
        "status": "assigned",
    }


@app.get("/matters")
def list_matters(role: Optional[str] = None, user_id: Optional[str] = None):
    """List all matters, optionally filtered by role/user."""
    matters = get_all_matters()
    if role == "junior" and user_id:
        matters = [m for m in matters if m.get("assigned_to") == user_id]
    elif role == "senior" and user_id:
        matters = [m for m in matters if m.get("senior_id") == user_id]
    # Sort newest first
    return sorted(matters, key=lambda m: m["updated_at"], reverse=True)


@app.get("/matters/{matter_id}")
def get_matter_detail(matter_id: str):
    matter = get_matter(matter_id)
    if not matter:
        raise HTTPException(404, f"Matter {matter_id} not found")
    return matter


@app.post("/matters/draft")
def submit_draft(req: SubmitDraftRequest):
    """
    Junior submits their draft.
    AI Supervisor immediately reviews it.
    If issues found → status = flagged. If clean → status = accepted.
    """
    matter = get_matter(req.matter_id)
    if not matter:
        raise HTTPException(404, "Matter not found")

    # Save draft
    update_matter(req.matter_id, draft=req.draft, status="ai_reviewing")
    add_action(
        req.matter_id,
        actor=req.junior_id,
        actor_type="human",
        role="junior",
        action="draft_submitted",
        detail=f"Junior submitted draft ({len(req.draft)} chars).",
    )

    # AI Supervisor reviews the draft
    task = f"Review this legal draft for the following matter:\n\nOriginal instructions: {matter['instructions']}\n\nDraft submitted:\n{req.draft}"
    context = f"Client: {matter['client']}. Matter type: {matter.get('matter_type','Commercial Contract Review')}."

    loop = asyncio.new_event_loop()
    async def run():
        tasks = [
            asyncio.to_thread(_run_agent, "review",        AgentRequest(task=task, context=context)),
            asyncio.to_thread(_run_agent, "risk_analysis", AgentRequest(task=task, context=context)),
        ]
        return await asyncio.gather(*tasks)
    review_result, risk_result = loop.run_until_complete(run())
    loop.close()

    # Supervisor check
    all_flags  = review_result.flags + risk_result.flags
    high_flags = [f for f in all_flags if str(f).upper().startswith("HIGH")]
    avg_conf   = (review_result.confidence + risk_result.confidence) // 2
    max_risk   = max(review_result.risk, risk_result.risk)

    ai_review = {
        "review":       review_result.dict(),
        "risk_analysis": risk_result.dict(),
        "overall_confidence": avg_conf,
        "overall_risk":       max_risk,
        "high_flag_count":    len(high_flags),
        "all_flags":          all_flags,
        "citations":          list(set(review_result.citations + risk_result.citations)),
    }

    add_action(
        req.matter_id,
        actor="supervisor_ai",
        actor_type="ai",
        role="supervisor_ai",
        action="reviewed",
        detail=f"AI review complete. Confidence: {avg_conf}%. Risk: {max_risk}%. High flags: {len(high_flags)}.",
    )

    # Decide: escalate or auto-approve
    if high_flags or max_risk > 50:
        update_matter(req.matter_id, status="flagged", ai_review=ai_review)
        add_action(
            req.matter_id,
            actor="supervisor_ai",
            actor_type="ai",
            role="supervisor_ai",
            action="flagged",
            detail=f"Flagged to senior: {len(high_flags)} HIGH flag(s), risk {max_risk}%. Requires senior review.",
        )
        return {"status": "flagged", "ai_review": ai_review, "matter_id": req.matter_id}
    else:
        update_matter(req.matter_id, status="accepted", ai_review=ai_review)
        add_action(
            req.matter_id,
            actor="supervisor_ai",
            actor_type="ai",
            role="supervisor_ai",
            action="auto_approved",
            detail=f"Auto-approved. No HIGH flags, risk {max_risk}% within threshold.",
        )
        return {"status": "accepted", "ai_review": ai_review, "matter_id": req.matter_id}


@app.post("/matters/decision")
def senior_decision(req: SeniorDecisionRequest):
    """
    Senior lawyer accepts or rejects the flagged matter.
    Reject → returns to junior for redraft.
    Accept → matter completed.
    """
    matter = get_matter(req.matter_id)
    if not matter:
        raise HTTPException(404, "Matter not found")

    if req.decision == "accepted":
        update_matter(req.matter_id, status="completed", senior_notes=req.notes)
        add_action(
            req.matter_id,
            actor=req.senior_id,
            actor_type="human",
            role="senior",
            action="accepted",
            detail=f"Senior accepted. Notes: {req.notes or 'None'}",
        )
        return {"status": "completed"}

    elif req.decision == "rejected":
        update_matter(req.matter_id, status="draft_submitted", senior_notes=req.notes)
        add_action(
            req.matter_id,
            actor=req.senior_id,
            actor_type="human",
            role="senior",
            action="rejected",
            detail=f"Senior rejected — returned to junior. Reason: {req.notes or 'No reason given'}",
        )
        return {"status": "returned_to_junior"}

    raise HTTPException(400, "decision must be 'accepted' or 'rejected'")


@app.post("/matters/generate_draft")
def generate_draft(req: GenerateDraftRequest):
    """
    Hybrid mode: AI drafting agent generates a draft for the junior to review/edit.
    Returns the draft text — junior can modify it before submitting.
    """
    matter = get_matter(req.matter_id)
    if not matter:
        raise HTTPException(404, "Matter not found")

    task = (
        f"Draft a professional legal response for the following matter.\n\n"
        f"Original partner instructions: {matter['instructions']}\n\n"
        f"Client: {matter['client']}. Matter type: {matter.get('matter_type','Commercial Contract Review')}."
    )
    routing = matter.get("routing", {})
    context = routing.get("instruction_to_junior", "")

    result = _run_agent("drafting", AgentRequest(task=task, context=context))

    add_action(
        req.matter_id,
        actor="drafting_ai",
        actor_type="ai",
        role="drafting_ai",
        action="ai_draft_generated",
        detail=f"AI generated draft for junior to review. Confidence: {result.confidence}%.",
    )

    return {
        "draft": result.output,
        "confidence": result.confidence,
        "citations": result.citations,
        "flags": result.flags,
    }


@app.post("/matters/autonomous")
def run_autonomous(req: AutonomousRequest):
    """
    Fully autonomous mode: AI does research + drafting + review + risk analysis.
    Sends final output directly to senior for approval — junior is the trigger only.
    """
    matter = get_matter(req.matter_id)
    if not matter:
        raise HTTPException(404, "Matter not found")

    task = (
        f"Complete the following legal matter end-to-end.\n\n"
        f"Instructions: {matter['instructions']}\n"
        f"Client: {matter['client']}. Matter type: {matter.get('matter_type','Commercial Contract Review')}."
    )

    add_action(
        req.matter_id,
        actor=req.junior_id,
        actor_type="human",
        role="junior",
        action="autonomous_triggered",
        detail="Junior triggered fully autonomous AI pipeline.",
    )
    update_matter(req.matter_id, status="ai_reviewing")

    # Run all 4 agents in parallel
    loop = asyncio.new_event_loop()
    async def run_all():
        return await asyncio.gather(
            asyncio.to_thread(_run_agent, "research",      AgentRequest(task=task)),
            asyncio.to_thread(_run_agent, "drafting",      AgentRequest(task=task)),
            asyncio.to_thread(_run_agent, "review",        AgentRequest(task=task)),
            asyncio.to_thread(_run_agent, "risk_analysis", AgentRequest(task=task)),
        )
    research_r, draft_r, review_r, risk_r = loop.run_until_complete(run_all())
    loop.close()

    # Save the AI-generated draft so the senior can see it
    ai_draft = (
        f"# AI-Generated Draft\n\n"
        f"## Research Summary\n{research_r.output}\n\n"
        f"## Drafted Clauses\n{draft_r.output}\n\n"
        f"## Review Notes\n{review_r.output}\n\n"
        f"## Risk Analysis\n{risk_r.output}"
    )

    all_flags  = review_r.flags + risk_r.flags + draft_r.flags
    high_flags = [f for f in all_flags if str(f).upper().startswith("HIGH")]
    avg_conf   = (research_r.confidence + draft_r.confidence + review_r.confidence + risk_r.confidence) // 4
    max_risk   = max(research_r.risk, draft_r.risk, review_r.risk, risk_r.risk)
    all_citations = list(set(research_r.citations + draft_r.citations + review_r.citations))

    ai_review = {
        "review":            review_r.dict(),
        "risk_analysis":     risk_r.dict(),
        "research":          research_r.dict(),
        "drafting":          draft_r.dict(),
        "overall_confidence": avg_conf,
        "overall_risk":       max_risk,
        "high_flag_count":    len(high_flags),
        "all_flags":          all_flags,
        "citations":          all_citations,
        "mode":              "autonomous",
    }

    add_action(
        req.matter_id,
        actor="supervisor_ai",
        actor_type="ai",
        role="supervisor_ai",
        action="autonomous_complete",
        detail=f"Full autonomous pipeline complete. Confidence: {avg_conf}%. Risk: {max_risk}%. High flags: {len(high_flags)}. Sent to senior for approval.",
    )

    # Always escalate to senior in autonomous mode — human must approve AI output
    update_matter(req.matter_id, draft=ai_draft, status="flagged", ai_review=ai_review)
    add_action(
        req.matter_id,
        actor="supervisor_ai",
        actor_type="ai",
        role="supervisor_ai",
        action="escalated_to_senior",
        detail="Autonomous output requires senior approval before delivery to client.",
    )

    return {
        "status": "awaiting_senior_approval",
        "ai_draft": ai_draft,
        "ai_review": ai_review,
        "matter_id": req.matter_id,
    }


class ChatRequest(BaseModel):
    matter_id: str
    junior_id: str
    message: str
    history: list = []      # list of {"role": "user"|"assistant", "content": "..."}


@app.post("/matters/chat")
def matter_chat(req: ChatRequest):
    """
    Per-matter AI chat assistant for the junior lawyer.
    The AI has full context of the matter and acts as a legal research/drafting assistant.
    """
    matter = get_matter(req.matter_id)
    if not matter:
        raise HTTPException(404, "Matter not found")

    routing = matter.get("routing", {})
    system_prompt = f"""You are an expert AI legal assistant helping a junior lawyer at a top UK law firm.
You are assisting with a specific assigned matter. Stay focused on this matter and give precise, actionable legal advice.

MATTER DETAILS:
- Matter ID: {matter['id']}
- Client: {matter['client']}
- Matter type: {matter.get('matter_type', 'Commercial Contract Review')}
- Instructions from partner: {matter['instructions']}
- Specific instruction to junior: {routing.get('instruction_to_junior', '')}

AI REVIEW (if available): {matter.get('ai_review') or 'Not yet reviewed'}

Your role:
- Answer legal research questions about this matter
- Help draft or improve specific clauses
- Explain relevant statutes (UCTA 1977, Sale of Goods Act etc.) and case law
- Point out risks and suggest how to address them
- Be concise and practical — this is a working lawyer, not a law student

Always ground your answers in specific UK law. Flag anything uncertain."""

    # Build messages including chat history
    messages = [{"role": "system", "content": system_prompt}]
    for h in req.history[-10:]:   # last 10 turns for context
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": req.message})

    stream = __import__('agents').client.chat.completions.create(
        model=__import__('agents').MODEL,
        messages=messages,
        temperature=0.5,
        max_tokens=1500,
        extra_body={
            "chat_template_kwargs": {"enable_thinking": True},
            "reasoning_budget": 1024,
        },
        stream=True,
    )
    response = ""
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta.content:
            response += delta.content

    add_action(
        req.matter_id,
        actor="assistant_ai",
        actor_type="ai",
        role="assistant_ai",
        action="chat_response",
        detail=f"Junior asked: {req.message[:80]}…",
    )

    return {"response": response}


@app.get("/team")
def get_team():
    return TEAM
