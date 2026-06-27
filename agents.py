"""
Legal AI Supervisor — agents.py

Four specialist agents + a supervisor loop, in plain Python.
ALL agents return structured JSON and go through the supervisor loop.

Architecture:
  Task → Supervisor → specialist agent → check thresholds
                    ↑___retry with feedback___|
                    → escalate to human after max_iterations
"""

import os
import json
import time
from datetime import datetime, timezone

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_URL = os.environ.get("BASE_URL", "https://integrate.api.nvidia.com/v1")
MODEL    = os.environ.get("MODEL_NAME", "nvidia/nemotron-3-ultra-550b-a55b")

# Load all available API keys — supports up to 3 keys
_keys = [k for k in [
    os.environ.get("NVIDIA_API_KEY") or os.environ.get("OPENAI_API_KEY"),
    os.environ.get("NVIDIA_API_KEY_2"),
    os.environ.get("NVIDIA_API_KEY_3"),
] if k]

if not _keys:
    raise RuntimeError("No API key found. Set NVIDIA_API_KEY in .env")

# One OpenAI client per key — round-robin across calls
_clients = [OpenAI(base_url=BASE_URL, api_key=k) for k in _keys]
_client_idx = 0

def _get_client() -> OpenAI:
    """Round-robin across available API keys to spread rate-limit load."""
    global _client_idx
    c = _clients[_client_idx % len(_clients)]
    _client_idx += 1
    return c

# Keep `client` as a convenience alias (used by api.py chat endpoint)
client = _clients[0]

# In-memory audit trail. A real version would write to Langfuse or a DB.
AUDIT_LOG = []


def log_event(agent: str, action: str, payload: dict):
    entry = {
        "id": f"{agent}_{int(time.time()*1000)}",
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        "agent": agent,
        "action": action,
        "payload": payload,
    }
    AUDIT_LOG.append(entry)
    return entry


# ---------------------------------------------------------------------------
# Agent system prompts — ALL agents return structured JSON
# ---------------------------------------------------------------------------
_JSON_SCHEMA = (
    'Respond with ONLY a valid JSON object, no markdown fences, no extra text. '
    'Use exactly this shape: '
    '{"output": "<your main response>", "confidence": <int 0-100>, '
    '"risk": <int 0-100>, "citations": ["..."], "flags": ["HIGH - ...", "MEDIUM - ...", "LOW - ..."]}. '
    "confidence = how sure you are your response is accurate and complete. "
    "risk = residual risk that something important is wrong or missing. "
    "citations = specific cases, statutes, or sources you referenced. "
    "flags = issues the supervising lawyer must be aware of, classified HIGH/MEDIUM/LOW."
)

AGENT_PROMPTS = {
    "research": (
        "You are a specialist legal research agent at a top-tier law firm. "
        "Research relevant case law, statutes, and legal principles for the given matter. "
        "Never fabricate citations — if unsure, mark as 'citation unverified'. "
        "Flag jurisdiction gaps and any areas where your knowledge may be outdated. "
        + _JSON_SCHEMA
    ),
    "drafting": (
        "You are a specialist legal drafting agent at a top-tier law firm. "
        "Draft precise, professional legal text based on the instructions. "
        "Flag every assumption a lawyer must verify. "
        "Mark jurisdiction-specific clauses explicitly. "
        + _JSON_SCHEMA
    ),
    "review": (
        "You are a specialist legal document review agent at a top-tier law firm. "
        "Review the given document or draft for errors, inconsistencies, missing clauses, and compliance gaps. "
        "List every issue found. Classify flags as HIGH / MEDIUM / LOW risk. "
        "Do not give a clean bill of health unless you are genuinely confident. "
        + _JSON_SCHEMA
    ),
    "risk_analysis": (
        "You are a specialist legal risk analysis agent at a top-tier law firm. "
        "Identify and assess legal risks. Every risk MUST be backed by a legal basis "
        "(statute, case law, or established principle). "
        "If no legal basis found, flag as 'UNVERIFIED — requires lawyer review'. "
        "Classify risks HIGH / MEDIUM / LOW. Over-flagging is better than missing a material risk. "
        + _JSON_SCHEMA
    ),
}


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------
def _extract_json(text: str) -> str:
    """Strip markdown fences if the model ignores instructions."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    # Find the outermost { ... }
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        return text[start:end]
    return text.strip()


def _call_agent(agent_name: str, task: str, context: str = "", feedback: str = "") -> tuple[str, str]:
    """
    Returns (output_text, reasoning_text).
    reasoning_text is the model's thinking chain — shown to the lawyer as transparency.
    """
    system_prompt = AGENT_PROMPTS[agent_name]
    user_content = f"TASK:\n{task}"
    if context:
        user_content += f"\n\nCONTEXT:\n{context}"
    if feedback:
        user_content += f"\n\nSUPERVISOR FEEDBACK (previous attempt failed):\n{feedback}\nAddress these issues directly."

    stream = _get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.6,
        top_p=0.95,
        max_tokens=4096,
        extra_body={
            "chat_template_kwargs": {"enable_thinking": True},
            "reasoning_budget": 4096,
        },
        stream=True,
    )

    output_text = ""
    reasoning_text = ""
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        reasoning = getattr(delta, "reasoning_content", None)
        if reasoning:
            reasoning_text += reasoning
        if delta.content:
            output_text += delta.content

    log_event(agent_name, "call", {
        "task_preview": task[:120],
        "output_preview": output_text[:300],
        "reasoning_preview": reasoning_text[:300],
    })
    return output_text, reasoning_text


def _supervisor_check(parsed: dict, confidence_threshold: int, risk_threshold: int) -> tuple[bool, list[str]]:
    """Returns (passed, list_of_issues)."""
    issues = []
    conf = parsed.get("confidence", 0)
    risk = parsed.get("risk", 100)
    flags = parsed.get("flags", [])

    if conf < confidence_threshold:
        issues.append(f"Confidence {conf}% below required {confidence_threshold}%")
    if risk > risk_threshold:
        issues.append(f"Risk {risk}% exceeds maximum {risk_threshold}%")
    high_flags = [f for f in flags if str(f).upper().startswith("HIGH")]
    if high_flags:
        issues.append(f"{len(high_flags)} HIGH-severity flag(s) flagged for human attention")

    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# Unified supervisor loop — use this from app.py
# ---------------------------------------------------------------------------
def run_supervised_task(
    agent_name: str,
    task: str,
    context: str = "",
    confidence_threshold: int = 80,
    risk_threshold: int = 20,
    max_iterations: int = 3,
) -> dict:
    """
    Run any specialist agent under supervisor control.
    Retries with feedback until thresholds are met, then escalates to human.

    Returns:
        status: "accepted" | "needs_human_review"
        attempt: number of attempts made
        result: the parsed JSON output from the agent
        history: list of all attempt results
    """
    feedback = ""
    history = []

    for attempt in range(1, max_iterations + 1):
        raw, reasoning = _call_agent(agent_name, task, context, feedback)

        try:
            parsed = json.loads(_extract_json(raw))
        except json.JSONDecodeError:
            log_event("supervisor", "parse_error", {"attempt": attempt, "raw": raw[:300]})
            feedback = "Your last response was not valid JSON. Return ONLY the JSON object described, no other text."
            history.append({"attempt": attempt, "parsed": None, "passed": False,
                            "issues": ["JSON parse error"], "reasoning": reasoning})
            continue

        # Attach reasoning to result so the UI can show the thinking chain
        parsed["_reasoning"] = reasoning

        passed, issues = _supervisor_check(parsed, confidence_threshold, risk_threshold)
        log_event("supervisor", "evaluate", {
            "attempt": attempt,
            "confidence": parsed.get("confidence"),
            "risk": parsed.get("risk"),
            "passed": passed,
            "issues": issues,
        })
        history.append({"attempt": attempt, "parsed": parsed, "passed": passed,
                        "issues": issues, "reasoning": reasoning})

        if passed:
            log_event("supervisor", "accept", {"attempt": attempt})
            return {"status": "accepted", "attempt": attempt, "result": parsed, "history": history}

        feedback = (
            f"Issues: {'; '.join(issues)}. "
            "Improve your grounding, add more citations, and reduce uncertainty. "
            "Return a revised JSON response."
        )

    log_event("supervisor", "escalate", {"reason": "threshold not met after max iterations",
                                          "final_issues": history[-1]["issues"]})
    return {
        "status": "needs_human_review",
        "attempt": max_iterations,
        "result": history[-1]["parsed"],
        "history": history,
        "escalation_reason": "; ".join(history[-1]["issues"]),
    }


# ---------------------------------------------------------------------------
# AI Router — assigns matters to the right lawyer
# ---------------------------------------------------------------------------
ROUTER_PROMPT = """You are an AI legal workflow router at a UK law firm.
Your job is to read a new client matter and assign it to the right lawyer.

IMPORTANT: You MUST use ONLY the exact IDs listed below. Do not invent IDs.

JUNIOR LAWYERS (use these exact IDs):
  junior_1 — Priya Patel, Contract Review specialist
  junior_2 — Tom Davies, Legal Research specialist
  junior_3 — Aisha Mensah, Corporate Drafting specialist

SENIOR LAWYERS (use these exact IDs):
  senior_1 — James Wright, Commercial Contracts specialist
  senior_2 — Meera Nair, Employment & IP specialist

Respond ONLY in valid JSON, no other text:
{
  "junior_id": "<must be one of: junior_1, junior_2, junior_3>",
  "junior_name": "<their full name>",
  "senior_id": "<must be one of: senior_1, senior_2>",
  "senior_name": "<their full name>",
  "matter_type": "<e.g. Commercial Contract Review, NDA, Employment Dispute>",
  "instruction_to_junior": "<clear one-paragraph instruction in plain legal English>",
  "reasoning": "<one sentence explaining why you chose this junior>"
}"""


def route_matter(instructions: str, client: str, team_summary: str) -> dict:
    """
    AI Router: reads the matter and assigns it to the right team member.
    Returns a parsed routing decision.
    """
    user_prompt = f"""CLIENT: {client}

INSTRUCTIONS FROM PARTNER:
{instructions}

TEAM STATUS:
{team_summary}

Assign this matter to the most appropriate junior lawyer."""

    raw, _ = _call_agent.__wrapped__(ROUTER_PROMPT, user_prompt) if hasattr(_call_agent, '__wrapped__') else _direct_llm_call(ROUTER_PROMPT, user_prompt)
    try:
        return json.loads(_extract_json(raw))
    except Exception:
        # Fallback to first junior
        return {
            "junior_id": "junior_1",
            "junior_name": "Priya Patel",
            "senior_id": "senior_1",
            "senior_name": "James Wright",
            "matter_type": "Commercial Contract Review",
            "instruction_to_junior": instructions,
            "reasoning": "Default assignment (router parse error)",
        }


def _direct_llm_call(system_prompt: str, user_prompt: str) -> tuple[str, str]:
    """Direct LLM call without agent wrapper — for the router."""
    stream = _get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=800,
        extra_body={
            "chat_template_kwargs": {"enable_thinking": True},
            "reasoning_budget": 512,
        },
        stream=True,
    )
    output, reasoning = "", ""
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        r = getattr(delta, "reasoning_content", None)
        if r: reasoning += r
        if delta.content: output += delta.content
    log_event("router_ai", "route", {"output_preview": output[:200]})
    return output, reasoning


# Patch route_matter to use _direct_llm_call properly
def route_matter(instructions: str, client: str, team_summary: str) -> dict:
    user_prompt = f"""CLIENT: {client}

INSTRUCTIONS FROM PARTNER:
{instructions}

TEAM STATUS:
{team_summary}

Assign this matter to the most appropriate junior lawyer."""

    raw, _ = _direct_llm_call(ROUTER_PROMPT, user_prompt)
    try:
        return json.loads(_extract_json(raw))
    except Exception:
        return {
            "junior_id": "junior_1",
            "junior_name": "Priya Patel",
            "senior_id": "senior_1",
            "senior_name": "James Wright",
            "matter_type": "Commercial Contract Review",
            "instruction_to_junior": instructions,
            "reasoning": "Default assignment (router parse error)",
        }


# ---------------------------------------------------------------------------
# Backward-compat shims (app.py v1 used these names)
# ---------------------------------------------------------------------------
def run_simple_agent(agent_name: str, task: str, context: str = "") -> dict:
    return run_supervised_task(agent_name, task, context)


def run_risk_analysis(task: str, confidence_threshold: int = 90,
                      risk_threshold: int = 10, max_iterations: int = 3) -> dict:
    return run_supervised_task("risk_analysis", task, "",
                               confidence_threshold, risk_threshold, max_iterations)


# ---------------------------------------------------------------------------
# CLI test: python agents.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Legal AI Supervisor — CLI Test ===\n")
    out = run_supervised_task(
        agent_name="risk_analysis",
        task="What are the key legal risks of a 12-month non-compete clause in an employment contract under English law?",
        context="Senior software engineer at a London fintech startup.",
        confidence_threshold=75,
        risk_threshold=25,
        max_iterations=3,
    )
    print(f"Status:   {out['status'].upper()}")
    print(f"Attempts: {out['attempt']}")
    if out.get("escalation_reason"):
        print(f"Escalation reason: {out['escalation_reason']}")
    r = out["result"] or {}
    print(f"\nConfidence: {r.get('confidence', '?')}%")
    print(f"Risk:       {r.get('risk', '?')}%")
    print(f"\n--- OUTPUT ---\n{r.get('output', '')}")
    print("\n--- FLAGS ---")
    for f in r.get("flags", []):
        print(f"  • {f}")
    print("\n--- CITATIONS ---")
    for c in r.get("citations", []):
        print(f"  • {c}")
    print(f"\nAudit log entries: {len(AUDIT_LOG)}")
