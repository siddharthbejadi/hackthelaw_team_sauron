"""
Legal AI Supervisor — Home / Live Demo
Shows real-time word-by-word streaming between AI agents.
"""
import streamlit as st
import json
import time
import os, sys

sys.path.insert(0, os.path.dirname(__file__))
from agents import _get_client, MODEL, AGENT_PROMPTS, _extract_json, log_event

st.set_page_config(page_title="Legal AI Supervisor", layout="wide", page_icon="⚖️")

st.markdown("""
<style>
.stApp { background:#eef2f7; }
section[data-testid="stSidebar"] { background:#e2e8f0; }
.stApp, .stApp p, .stApp span, .stApp div, .stApp label,
.stApp .stMarkdown, .stApp .stText { color:#111 !important; }
.stApp h1, .stApp h2, .stApp h3 { color:#0f172a !important; }

.msg-supervisor {
    background:#f5f3ff; border-left:3px solid #7c3aed;
    border-radius:0 8px 8px 0; padding:10px 14px; margin:4px 0;
    font-size:0.82rem; color:#1e1b4b;
}
.msg-research {
    background:#eff6ff; border-left:3px solid #2563eb;
    border-radius:0 8px 8px 0; padding:10px 14px; margin:4px 0;
    font-size:0.82rem; color:#1e3a5f;
}
.msg-review {
    background:#fffbeb; border-left:3px solid #d97706;
    border-radius:0 8px 8px 0; padding:10px 14px; margin:4px 0;
    font-size:0.82rem; color:#451a03;
}
.msg-risk {
    background:#fff1f2; border-left:3px solid #dc2626;
    border-radius:0 8px 8px 0; padding:10px 14px; margin:4px 0;
    font-size:0.82rem; color:#450a0a;
}
.msg-drafting {
    background:#faf5ff; border-left:3px solid #9333ea;
    border-radius:0 8px 8px 0; padding:10px 14px; margin:4px 0;
    font-size:0.82rem; color:#3b0764;
}
.agent-label {
    font-size:0.65rem; font-weight:700; letter-spacing:.8px;
    text-transform:uppercase; margin-bottom:4px;
}
.arrow-line {
    color:#94a3b8; font-size:0.72rem; padding:2px 0 2px 16px;
    display:block;
}
.pill {
    border-radius:4px; padding:3px 10px; font-size:0.75rem; font-weight:700;
}
#MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:20px 0 10px;">
  <div style="font-size:2.4rem;font-weight:800;color:#0f172a;letter-spacing:-0.5px;">⚖️ Legal AI Supervisor</div>
  <div style="color:#64748b;font-size:0.9rem;margin-top:6px;">
    Watch AI agents communicate in real time — research, draft, review, and risk analysis running live.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Mode selector ──────────────────────────────────────────────────────────────
col_mode, col_info = st.columns([2, 3])
with col_mode:
    demo_mode = st.radio(
        "Pipeline mode",
        ["⚡ Review + Risk (fast)", "🔬 Full: Research + Draft + Review + Risk"],
        label_visibility="collapsed",
        horizontal=False,
    )
full_pipeline = "Full" in demo_mode

with col_info:
    st.markdown(
        f'<div style="background:#fff;border:1px solid #cbd5e1;border-radius:8px;padding:10px 14px;font-size:0.78rem;color:#475569;">'
        f'{"<b style=\'color:#7c3aed\'>Full pipeline</b>: Research → Draft → Review → Risk → Supervisor decision" if full_pipeline else "<b style=\'color:#2563eb\'>Fast pipeline</b>: Review → Risk → Supervisor decision"}'
        f'<br>All agents use <span style="color:#2563eb;">NVIDIA Nemotron-Ultra</span> with thinking tokens enabled.</div>',
        unsafe_allow_html=True,
    )

st.markdown("")

# ── Task input ─────────────────────────────────────────────────────────────────
task = st.chat_input("Describe the legal matter or paste a clause for analysis…")

# ── Streaming helpers ──────────────────────────────────────────────────────────
AGENT_META = {
    "research":    {"label": "🔍 RESEARCH AGENT",  "css": "msg-research",  "color": "#2563eb"},
    "drafting":    {"label": "✍️ DRAFTING AGENT",  "css": "msg-drafting",  "color": "#9333ea"},
    "review":      {"label": "🔎 REVIEW AGENT",    "css": "msg-review",    "color": "#d97706"},
    "risk_analysis":{"label":"⚠️ RISK AGENT",      "css": "msg-risk",      "color": "#dc2626"},
    "supervisor":  {"label": "🧠 SUPERVISOR",      "css": "msg-supervisor","color": "#7c3aed"},
}

def stream_agent_live(agent_name: str, task: str, context: str = ""):
    """
    Call a specialist agent and stream its output token by token.
    Returns (full_output_text, parsed_json).
    Updates the provided Streamlit placeholder in real time.
    """
    system_prompt = AGENT_PROMPTS[agent_name]
    user_content  = f"TASK:\n{task}"
    if context:
        user_content += f"\n\nCONTEXT:\n{context}"

    stream = _get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_content},
        ],
        temperature=0.6,
        top_p=0.95,
        max_tokens=3000,
        extra_body={
            "chat_template_kwargs": {"enable_thinking": True},
            "reasoning_budget": 2048,
        },
        stream=True,
    )

    output_text    = ""
    reasoning_text = ""
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        r = getattr(delta, "reasoning_content", None)
        if r:
            reasoning_text += r
        if delta.content:
            output_text += delta.content
            yield delta.content   # yield each token for live display

    log_event(agent_name, "live_stream", {"task_preview": task[:80]})
    return output_text


def parse_agent_output(raw: str) -> dict:
    try:
        return json.loads(_extract_json(raw))
    except Exception:
        return {"output": raw, "confidence": 0, "risk": 100, "citations": [], "flags": []}


def supervisor_message(placeholder, msg: str):
    meta = AGENT_META["supervisor"]
    placeholder.markdown(
        f'<div class="{meta["css"]}">'
        f'<div class="agent-label" style="color:{meta["color"]};">{meta["label"]}</div>'
        f'{msg}</div>',
        unsafe_allow_html=True,
    )


def render_agent_stream(agent_name: str, task: str, context: str = ""):
    """
    Renders one agent's live stream in the Streamlit UI.
    Returns the parsed JSON result.
    """
    meta   = AGENT_META[agent_name]
    col_l, col_r = st.columns([1, 12])
    with col_r:
        st.markdown(
            f'<div class="agent-label" style="color:{meta["color"]};margin-bottom:4px;">'
            f'{meta["label"]} <span style="color:#94a3b8;font-size:0.6rem;font-weight:400;">NVIDIA Nemotron-Ultra · streaming…</span></div>',
            unsafe_allow_html=True,
        )
        box = st.empty()

    full_text = ""
    for token in stream_agent_live(agent_name, task, context):
        full_text += token
        # Show streaming text (strip JSON boilerplate for readability)
        display = full_text.lstrip("{\" \n")
        box.markdown(
            f'<div class="{meta["css"]}" style="border-left-color:{meta["color"]};">'
            f'{display[:600]}{"…" if len(display)>600 else "▌"}</div>',
            unsafe_allow_html=True,
        )

    parsed = parse_agent_output(full_text)

    # Final clean render with result pills
    conf    = parsed.get("confidence", "—")
    risk    = parsed.get("risk", "—")
    flags   = parsed.get("flags", [])
    high_n  = len([f for f in flags if "HIGH" in str(f).upper()])
    cites   = parsed.get("citations", [])
    output  = parsed.get("output", full_text)[:300]

    conf_c = "#16a34a" if isinstance(conf,int) and conf>=70 else "#d97706" if isinstance(conf,int) and conf>=50 else "#dc2626"
    risk_c = "#dc2626" if isinstance(risk,int) and risk>60 else "#d97706" if isinstance(risk,int) and risk>30 else "#16a34a"

    pills = (
        f'<span class="pill" style="background:{conf_c}18;color:{conf_c};border:1px solid {conf_c}44;">conf {conf}%</span>'
        f'<span class="pill" style="background:{risk_c}18;color:{risk_c};border:1px solid {risk_c}44;">risk {risk}%</span>'
        + (f'<span class="pill" style="background:#fef2f2;color:#dc2626;border:1px solid #fca5a5;">⚑ {high_n} HIGH</span>' if high_n else "")
        + (f'<span class="pill" style="background:#eff6ff;color:#2563eb;border:1px solid #93c5fd;">{len(cites)} citation(s)</span>' if cites else "")
    )

    box.markdown(
        f'<div class="{meta["css"]}" style="border-left-color:{meta["color"]};">'
        f'<div style="color:#374151;line-height:1.5;margin-bottom:8px;">{output}{"…" if len(parsed.get("output",""))>300 else ""}</div>'
        f'<div style="display:flex;gap:6px;flex-wrap:wrap;">{pills}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    return parsed


# ── Main pipeline ──────────────────────────────────────────────────────────────
if task:
    st.markdown("---")
    st.markdown(
        '<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">'
        '<span style="background:#fef2f2;color:#dc2626;border:1px solid #fca5a5;border-radius:4px;padding:2px 10px;font-size:0.68rem;font-weight:700;letter-spacing:1px;">● LIVE</span>'
        '<span style="color:#0f172a;font-weight:700;">Agent Communication Pipeline</span>'
        '<span style="color:#94a3b8;font-size:0.75rem;margin-left:4px;">— real-time output from each specialist agent</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    results = {}

    # ── SUPERVISOR: open ──────────────────────────────────────────────────
    sup_open = st.empty()
    supervisor_message(sup_open,
        f'<span style="color:#7c3aed;">Received task.</span> Routing to '
        f'{"4 specialist agents" if full_pipeline else "2 specialist agents"} — '
        f'each will stream their analysis live below. Task: <em style="color:#64748b;">{task[:80]}{"…" if len(task)>80 else ""}</em>'
    )

    agent_order = (
        ["research", "drafting", "review", "risk_analysis"]
        if full_pipeline else
        ["review", "risk_analysis"]
    )

    # ── Run each agent ────────────────────────────────────────────────────
    for agent_name in agent_order:
        meta = AGENT_META[agent_name]

        # Supervisor sends message to agent
        send_placeholder = st.empty()
        send_placeholder.markdown(
            f'<span class="arrow-line">'
            f'<span style="color:#7c3aed;">🧠 Supervisor</span>'
            f' → <span style="color:{meta["color"]};">{meta["label"]}</span>'
            f': <em style="color:#94a3b8;">sending task context…</em>'
            f'</span>',
            unsafe_allow_html=True,
        )

        # Agent streams its response
        parsed = render_agent_stream(agent_name, task)
        results[agent_name] = parsed

        # Agent replies to supervisor
        send_placeholder.markdown(
            f'<span class="arrow-line">'
            f'<span style="color:{meta["color"]};">{meta["label"]}</span>'
            f' → <span style="color:#7c3aed;">🧠 Supervisor</span>'
            f': <em style="color:#94a3b8;">complete · conf {parsed.get("confidence","?")}% · risk {parsed.get("risk","?")}%</em>'
            f'</span>',
            unsafe_allow_html=True,
        )

    # ── SUPERVISOR: decision ──────────────────────────────────────────────
    all_flags  = [f for r in results.values() for f in r.get("flags", [])]
    high_flags = [f for f in all_flags if "HIGH" in str(f).upper()]
    confs      = [r.get("confidence", 0) for r in results.values() if isinstance(r.get("confidence"), int)]
    risks      = [r.get("risk", 0)       for r in results.values() if isinstance(r.get("risk"), int)]
    all_cites  = list({c for r in results.values() for c in r.get("citations", [])})

    avg_conf  = sum(confs) // len(confs) if confs else 0
    max_risk  = max(risks) if risks else 0
    escalate  = bool(high_flags) or max_risk > 50

    conf_c = "#16a34a" if avg_conf >= 70 else "#d97706" if avg_conf >= 50 else "#dc2626"
    risk_c = "#dc2626" if max_risk > 60 else "#d97706" if max_risk > 30 else "#16a34a"

    st.markdown(
        f'<span class="arrow-line" style="color:#7c3aed;">All agents → 🧠 Supervisor: results aggregated</span>',
        unsafe_allow_html=True,
    )

    decision_color = "#dc2626" if escalate else "#16a34a"
    decision_label = "ESCALATE → Senior Lawyer" if escalate else "APPROVE — no HIGH flags"
    decision_reason = (
        f"{len(high_flags)} HIGH flag(s), risk {max_risk}% exceeds threshold"
        if escalate else
        f"No HIGH flags, risk {max_risk}% within threshold"
    )

    sup_close = st.empty()
    sup_close.markdown(
        f'<div class="msg-supervisor" style="border-left-color:{decision_color};">'
        f'<div class="agent-label" style="color:#7c3aed;">🧠 SUPERVISOR DECISION</div>'
        f'<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:8px;">'
        f'<span class="pill" style="background:{conf_c}18;color:{conf_c};border:1px solid {conf_c}44;">confidence {avg_conf}%</span>'
        f'<span class="pill" style="background:{risk_c}18;color:{risk_c};border:1px solid {risk_c}44;">risk {max_risk}%</span>'
        f'<span class="pill" style="background:#fef2f2;color:#dc2626;border:1px solid #fca5a5;">{len(high_flags)} HIGH flag(s)</span>'
        f'<span class="pill" style="background:#eff6ff;color:#2563eb;border:1px solid #93c5fd;">{len(all_cites)} citation(s)</span>'
        f'</div>'
        f'<div style="font-size:1rem;font-weight:700;color:{decision_color};">→ {decision_label}</div>'
        f'<div style="font-size:0.75rem;color:#64748b;margin-top:3px;">{decision_reason}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Expandable detail sections ────────────────────────────────────────
    if high_flags:
        with st.expander(f"⚑ {len(high_flags)} HIGH flags raised", expanded=True):
            for f in high_flags[:6]:
                st.markdown(f'<div style="font-size:0.78rem;color:#dc2626;background:#fef2f2;border-radius:4px;padding:6px 10px;margin:3px 0;border-left:2px solid #dc2626;">⚑ {f}</div>', unsafe_allow_html=True)

    if all_cites:
        with st.expander(f"📚 {len(all_cites)} citations verified by AI"):
            for c in all_cites[:8]:
                st.markdown(f"- [{c}](https://www.google.com/search?q={c.replace(' ','+')}+UK+case+law)")

    st.markdown(
        '<div style="margin-top:16px;font-size:0.72rem;color:#94a3b8;text-align:center;">'
        'Go to <b>Partner</b> → submit as a tracked matter · <b>Dashboard</b> → see full pipeline with audit trail'
        '</div>',
        unsafe_allow_html=True,
    )

else:
    # ── Landing state ─────────────────────────────────────────────────────
    st.markdown("""
<div style="max-width:960px;margin:48px auto;text-align:center;padding:0 16px;">
  <div style="font-size:4rem;margin-bottom:20px;">⚖️</div>
  <div style="color:#000;font-size:1.25rem;font-weight:700;margin-bottom:10px;">
    AI-Powered Legal Supervision
  </div>
  <div style="color:#1e293b;font-size:0.95rem;line-height:1.8;margin-bottom:40px;max-width:580px;margin-left:auto;margin-right:auto;">
    Type a legal clause, matter description, or question above.<br>
    Watch <b style="color:#2563eb;">AI agents</b> stream their analysis live —
    each one thinking, writing, and handing results to the next.
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;max-width:900px;margin:0 auto 40px;">
    <div style="background:#fff;border-left:4px solid #2563eb;border-radius:8px;padding:24px 16px;font-size:0.85rem;color:#000;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
      <div style="font-size:1.8rem;margin-bottom:10px;">🔍</div>
      <div style="color:#2563eb;font-weight:700;font-size:0.9rem;margin-bottom:8px;">Research</div>
      Finds relevant UK statutes and case law
    </div>
    <div style="background:#fff;border-left:4px solid #d97706;border-radius:8px;padding:24px 16px;font-size:0.85rem;color:#000;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
      <div style="font-size:1.8rem;margin-bottom:10px;">✍️</div>
      <div style="color:#d97706;font-weight:700;font-size:0.9rem;margin-bottom:8px;">Drafting</div>
      Drafts clauses and legal documents
    </div>
    <div style="background:#fff;border-left:4px solid #dc2626;border-radius:8px;padding:24px 16px;font-size:0.85rem;color:#000;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
      <div style="font-size:1.8rem;margin-bottom:10px;">🔎</div>
      <div style="color:#dc2626;font-weight:700;font-size:0.9rem;margin-bottom:8px;">Review + Risk</div>
      Checks compliance and flags HIGH risks
    </div>
    <div style="background:#fff;border-left:4px solid #7c3aed;border-radius:8px;padding:24px 16px;font-size:0.85rem;color:#000;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
      <div style="font-size:1.8rem;margin-bottom:10px;">🧠</div>
      <div style="color:#7c3aed;font-weight:700;font-size:0.9rem;margin-bottom:8px;">Supervisor</div>
      Aggregates results and decides escalation
    </div>
  </div>
  <div style="display:flex;justify-content:center;gap:24px;flex-wrap:wrap;margin-bottom:32px;">
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:12px 20px;font-size:0.8rem;color:#000;">
      <b style="color:#0f172a;">Partner</b> — Submit matters
    </div>
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:12px 20px;font-size:0.8rem;color:#000;">
      <b style="color:#0f172a;">Junior</b> — Write with AI assistance
    </div>
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:12px 20px;font-size:0.8rem;color:#000;">
      <b style="color:#0f172a;">Senior</b> — Approve or escalate
    </div>
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:12px 20px;font-size:0.8rem;color:#000;">
      <b style="color:#0f172a;">Dashboard</b> — Full audit trail
    </div>
  </div>
  <div style="font-size:0.75rem;color:#94a3b8;">
    Powered by NVIDIA Nemotron-Ultra 550B · Clifford Chance Hackathon
  </div>
</div>
""", unsafe_allow_html=True)
