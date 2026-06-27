"""
viz.py — Agent pipeline visualization.
Generates self-contained animated HTML for any matter.
Import: from viz import build_matter_flow_html
"""

def build_matter_flow_html(matter: dict) -> str:
    actions    = matter.get("actions", [])
    routing    = matter.get("routing", {})
    ai_review  = matter.get("ai_review") or {}
    status     = matter["status"]

    review_r   = ai_review.get("review", {})
    risk_r     = ai_review.get("risk_analysis", {})
    research_r = ai_review.get("research", {})
    drafting_r = ai_review.get("drafting", {})
    overall_conf  = ai_review.get("overall_confidence", "—")
    overall_risk  = ai_review.get("overall_risk", "—")
    high_flags    = ai_review.get("high_flag_count", 0)
    all_flags     = ai_review.get("all_flags", [])
    citations     = ai_review.get("citations", [])
    is_auto       = ai_review.get("mode") == "autonomous"
    has_ai_output = bool(review_r or risk_r or research_r or drafting_r)

    def _act(role):
        for a in actions:
            if a["role"] == role:
                return a
        return {}

    partner_act = _act("partner")
    router_act  = _act("router_ai")
    junior_act  = _act("junior")
    senior_act  = _act("senior")

    # ── HTML helpers ──────────────────────────────────────────────────────
    def badge_html(is_ai):
        if is_ai:
            return '<span style="background:#eff6ff;color:#2563eb;border-radius:3px;padding:1px 7px;font-size:0.62rem;font-weight:700;letter-spacing:.5px;">🤖 AI</span>'
        return '<span style="background:#f0fdf4;color:#16a34a;border-radius:3px;padding:1px 7px;font-size:0.62rem;font-weight:700;letter-spacing:.5px;">✋ Human</span>'

    def model_tag(name):
        return f'<span style="background:#f8fafc;color:#64748b;border-radius:3px;padding:1px 6px;font-size:0.6rem;border:1px solid #e2e8f0;">{name}</span>'

    def conf_pill(val, label="conf"):
        if val == "—" or val is None:
            return ""
        try:
            v = int(val)
            c = "#16a34a" if v >= 70 else "#d97706" if v >= 50 else "#dc2626"
            bg = "#f0fdf4" if v >= 70 else "#fffbeb" if v >= 50 else "#fef2f2"
            return f'<span style="background:{bg};color:{c};border-radius:3px;padding:1px 6px;font-size:0.62rem;border:1px solid {c}44;">{label}: {v}%</span>'
        except Exception:
            return ""

    def risk_pill(val):
        if val == "—" or val is None:
            return ""
        try:
            v = int(val)
            c = "#16a34a" if v <= 30 else "#d97706" if v <= 60 else "#dc2626"
            bg = "#f0fdf4" if v <= 30 else "#fffbeb" if v <= 60 else "#fef2f2"
            return f'<span style="background:{bg};color:{c};border-radius:3px;padding:1px 6px;font-size:0.62rem;border:1px solid {c}44;">risk: {v}%</span>'
        except Exception:
            return ""

    def card(icon, title, subtitle, body_html, is_ai=True, border_color=None, model=None, pills="", glow=True):
        bc = border_color or ("#2563eb" if is_ai else "#16a34a")
        gw = f"0 0 16px {bc}18" if glow else "none"
        mod = f"&nbsp;&nbsp;{model_tag(model)}" if model else ""
        return f"""
<div style="
    display:flex;gap:14px;align-items:flex-start;
    background:#fff;
    border:1px solid #e2e8f0;border-left:3px solid {bc};
    border-radius:10px;padding:14px 16px;
    box-shadow:{gw};
    position:relative;
">
  <div style="font-size:2rem;min-width:40px;text-align:center;line-height:1.2;padding-top:2px;">{icon}</div>
  <div style="flex:1;min-width:0;">
    <div style="display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:6px;">
      {badge_html(is_ai)}
      <span style="font-weight:700;color:#0f172a;font-size:0.9rem;">{title}</span>
      <span style="color:#64748b;font-size:0.75rem;">{subtitle}</span>
      {mod}
    </div>
    <div style="font-size:0.78rem;color:#475569;line-height:1.55;">{body_html}</div>
    {f'<div style="display:flex;gap:5px;flex-wrap:wrap;margin-top:8px;">{pills}</div>' if pills else ''}
  </div>
</div>"""

    def connector(label="", color="#cbd5e1", animated=False):
        anim = "animation:pulse 2s ease-in-out infinite;" if animated else ""
        return f"""
<div style="display:flex;align-items:flex-start;gap:10px;padding:0 0 0 58px;margin:0;">
  <div style="display:flex;flex-direction:column;align-items:center;">
    <div style="width:2px;height:28px;background:{color};{anim}"></div>
    <div style="color:{color};font-size:0.6rem;margin-top:-3px;">▼</div>
  </div>
  {f'<span style="font-size:0.62rem;color:#94a3b8;margin-top:4px;white-space:nowrap;">{label}</span>' if label else ''}
</div>"""

    def parallel_block():
        """Side-by-side agent cards for parallel execution."""
        agents = []

        if research_r:
            c = research_r.get("confidence", "—")
            out = str(research_r.get("output", ""))[:130]
            cites = research_r.get("citations", [])
            agents.append(f"""
<div style="flex:1;min-width:140px;background:#eff6ff;border:1px solid #bfdbfe;border-top:2px solid #2563eb;border-radius:8px;padding:10px;">
  <div style="font-size:0.68rem;font-weight:700;color:#2563eb;margin-bottom:5px;">🔍 RESEARCH</div>
  <div style="font-size:0.7rem;color:#64748b;margin-bottom:6px;">{model_tag("NVIDIA Nemotron-Ultra")}</div>
  <div style="font-size:0.68rem;color:#475569;line-height:1.4;margin-bottom:6px;">{out}{"…" if len(out)==130 else ""}</div>
  {conf_pill(c)}
  <div style="font-size:0.62rem;color:#94a3b8;margin-top:4px;">{len(cites)} citation(s) found</div>
</div>""")

        if drafting_r:
            c = drafting_r.get("confidence", "—")
            out = str(drafting_r.get("output", ""))[:130]
            agents.append(f"""
<div style="flex:1;min-width:140px;background:#faf5ff;border:1px solid #e9d5ff;border-top:2px solid #9333ea;border-radius:8px;padding:10px;">
  <div style="font-size:0.68rem;font-weight:700;color:#9333ea;margin-bottom:5px;">✍️ DRAFTING</div>
  <div style="font-size:0.7rem;color:#64748b;margin-bottom:6px;">{model_tag("NVIDIA Nemotron")}</div>
  <div style="font-size:0.68rem;color:#475569;line-height:1.4;margin-bottom:6px;">{out}{"…" if len(out)==130 else ""}</div>
  {conf_pill(c)}
</div>""")

        if review_r:
            c = review_r.get("confidence", "—")
            r = review_r.get("risk", "—")
            out = str(review_r.get("output", ""))[:130]
            nflags = len([f for f in review_r.get("flags", []) if "HIGH" in str(f).upper()])
            agents.append(f"""
<div style="flex:1;min-width:140px;background:#fffbeb;border:1px solid #fde68a;border-top:2px solid #d97706;border-radius:8px;padding:10px;">
  <div style="font-size:0.68rem;font-weight:700;color:#d97706;margin-bottom:5px;">🔎 REVIEW</div>
  <div style="font-size:0.7rem;color:#64748b;margin-bottom:6px;">{model_tag("NVIDIA Nemotron")}</div>
  <div style="font-size:0.68rem;color:#475569;line-height:1.4;margin-bottom:6px;">{out}{"…" if len(out)==130 else ""}</div>
  <div style="display:flex;gap:4px;flex-wrap:wrap;">{conf_pill(c)}{risk_pill(r)}</div>
  {f'<div style="font-size:0.62rem;color:#dc2626;margin-top:4px;">{nflags} HIGH flag(s)</div>' if nflags else ""}
</div>""")

        if risk_r:
            r = risk_r.get("risk", "—")
            out = str(risk_r.get("output", ""))[:130]
            nflags = len([f for f in risk_r.get("flags", []) if "HIGH" in str(f).upper()])
            agents.append(f"""
<div style="flex:1;min-width:140px;background:#fef2f2;border:1px solid #fecaca;border-top:2px solid #dc2626;border-radius:8px;padding:10px;">
  <div style="font-size:0.68rem;font-weight:700;color:#dc2626;margin-bottom:5px;">⚠️ RISK</div>
  <div style="font-size:0.7rem;color:#64748b;margin-bottom:6px;">{model_tag("NVIDIA Nemotron")}</div>
  <div style="font-size:0.68rem;color:#475569;line-height:1.4;margin-bottom:6px;">{out}{"…" if len(out)==130 else ""}</div>
  {risk_pill(r)}
  {f'<div style="font-size:0.62rem;color:#dc2626;margin-top:4px;">{nflags} HIGH flag(s)</div>' if nflags else ""}
</div>""")

        if not agents:
            return ""

        n = len(agents)
        label = f"Spawned {n} specialist agent{'s' if n>1 else ''} in parallel → results aggregated by supervisor"
        return f"""
<div style="padding:0 0 0 58px;margin:4px 0;">
  <div style="font-size:0.62rem;color:#2563eb;margin-bottom:8px;letter-spacing:.3px;">⚡ {label}</div>
  <div style="display:flex;gap:8px;flex-wrap:wrap;">{"".join(agents)}</div>
</div>"""

    # ── Flags + citations ─────────────────────────────────────────────────
    flags_html = ""
    if all_flags:
        items = []
        for f in all_flags[:5]:
            fu = str(f).upper()
            fc = "#dc2626" if fu.startswith("HIGH") else "#d97706" if fu.startswith("MEDIUM") else "#2563eb"
            bg = "#fef2f2" if fu.startswith("HIGH") else "#fffbeb" if fu.startswith("MEDIUM") else "#eff6ff"
            items.append(f'<div style="font-size:0.7rem;color:{fc};background:{bg};border-radius:4px;padding:4px 8px;margin:2px 0;border-left:2px solid {fc};">⚑ {str(f)[:120]}</div>')
        flags_html = "".join(items)
        if len(all_flags) > 5:
            flags_html += f'<div style="font-size:0.65rem;color:#94a3b8;margin-top:2px;">…and {len(all_flags)-5} more flag(s)</div>'

    cite_html = ""
    if citations:
        items = [f'<span style="font-size:0.65rem;color:#2563eb;background:#eff6ff;border:1px solid #bfdbfe;border-radius:3px;padding:2px 7px;">{c[:60]}</span>' for c in citations[:5]]
        cite_html = f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:6px;">{"".join(items)}</div>'

    # ── Build pipeline ────────────────────────────────────────────────────
    steps = ""

    # 1. PARTNER
    steps += card(
        "👔", "PARTNER", "Human",
        f"<b>Client:</b> {matter.get('client','—')} &nbsp;|&nbsp; <b>Matter:</b> {matter.get('matter_type','—')}<br>"
        f"<b>Submitted:</b> {matter.get('created_at','')[:16]}",
        is_ai=False,
        pills=conf_pill(None)
    )
    steps += connector("Partner instructions →  AI Router", "#16a34a")

    # 2. AI ROUTER
    steps += card(
        "🤖", "AI ROUTER", "Workload-aware assignment",
        f"<b>Junior assigned:</b> {routing.get('junior_name','—')} "
        f"<span style='color:#64748b;font-size:0.72rem;'>({routing.get('matter_type','—')})</span><br>"
        f"<b>Senior supervisor:</b> {routing.get('senior_name','—')}<br>"
        f"<b>Reasoning:</b> {routing.get('reasoning','—')[:120]}",
        is_ai=True,
        model="NVIDIA Nemotron-Ultra",
        border_color="#2563eb"
    )
    steps += connector("Assignment + instructions →  Junior Lawyer", "#2563eb")

    # 3. JUNIOR
    mode_label = ""
    if junior_act:
        action_name = junior_act.get("action", "")
        if "autonomous" in action_name:
            mode_label = '<span style="background:#faf5ff;color:#9333ea;border:1px solid #e9d5ff;border-radius:3px;padding:1px 7px;font-size:0.62rem;margin-left:6px;">🤖 Autonomous Mode</span>'
        elif is_auto:
            mode_label = '<span style="background:#faf5ff;color:#9333ea;border:1px solid #e9d5ff;border-radius:3px;padding:1px 7px;font-size:0.62rem;margin-left:6px;">🤖 Autonomous Mode</span>'
        else:
            ai_drafted = ai_review.get("mode") == "hybrid"
            if ai_drafted:
                mode_label = '<span style="background:#eff6ff;color:#2563eb;border:1px solid #bfdbfe;border-radius:3px;padding:1px 7px;font-size:0.62rem;margin-left:6px;">🤝 Hybrid Mode</span>'
            else:
                mode_label = '<span style="background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0;border-radius:3px;padding:1px 7px;font-size:0.62rem;margin-left:6px;">✋ Manual Mode</span>'

    junior_body = (
        f"{junior_act.get('detail','Awaiting draft…')}{mode_label}"
        if junior_act else "⏳ Awaiting draft submission…"
    )
    steps += card(
        "📝", "JUNIOR LAWYER", routing.get("junior_name", "—"),
        junior_body,
        is_ai=False,
        border_color="#16a34a" if junior_act else "#94a3b8"
    )

    if has_ai_output:
        steps += connector("Draft →  AI Supervisor (for review)", "#7c3aed")

        # 4. AI SUPERVISOR header
        sup_body = (
            f"Orchestrating <b>{2 if not is_auto else 4}</b> specialist agent(s) in parallel<br>"
            f"<b>Aggregate confidence:</b> {overall_conf}% &nbsp; "
            f"<b>Max risk:</b> {overall_risk}% &nbsp; "
            f"<b>HIGH flags:</b> {high_flags}"
        )
        steps += card(
            "🧠", "AI SUPERVISOR", "Orchestrator + quality gate",
            sup_body,
            is_ai=True,
            model="NVIDIA Nemotron-Ultra",
            border_color="#7c3aed"
        )

        # 4b. Parallel agents
        steps += parallel_block()

        # 4c. Supervisor decision
        steps += connector("Aggregated results →  decision", "#7c3aed", animated=True)

        if high_flags > 0 or (isinstance(overall_risk, int) and overall_risk > 50):
            escalate_body = (
                f"<b>Trigger:</b> {high_flags} HIGH flag(s) &nbsp;|&nbsp; Risk {overall_risk}% exceeds threshold<br>"
                f"<b>Action:</b> Escalating to senior lawyer — human decision required<br><br>"
                f"{flags_html}"
                f"<div style='margin-top:8px;'><b style='font-size:0.72rem;color:#64748b;'>Citations verified by AI:</b>{cite_html}</div>"
            )
            steps += card(
                "🚩", "ESCALATION", "Supervisor → Senior Lawyer",
                escalate_body,
                is_ai=True,
                border_color="#dc2626"
            )
        else:
            steps += card(
                "✅", "AUTO-APPROVED", "No escalation needed",
                "No HIGH flags detected. Risk within threshold. Draft approved automatically — client delivery ready.",
                is_ai=True,
                border_color="#16a34a"
            )

        steps += connector("AI summary + flags + citations →  Senior", "#d97706")

    # 5. SENIOR
    if senior_act:
        dec = senior_act.get("action", "—")
        dc = "#16a34a" if dec == "accepted" else "#dc2626"
        dec_body = (
            f"<b>Decision:</b> <span style='color:{dc};font-weight:700;font-size:0.9rem;'>{dec.upper()}</span><br>"
            f"{senior_act.get('detail','')[:180]}"
        )
        steps += card(
            "✅" if dec == "accepted" else "↩️",
            "SENIOR LAWYER", routing.get("senior_name", "Senior"),
            dec_body,
            is_ai=False,
            border_color=dc
        )
        if dec == "accepted":
            steps += connector("Approved →  Dashboard / Client delivery", "#16a34a")
            steps += card("📊", "DASHBOARD", "Completed — full audit trail preserved",
                          "Matter closed. Every action (Human ✋ / AI 🤖) logged with timestamps, confidence scores, and citations.",
                          is_ai=False, border_color="#16a34a", glow=False)
    elif status == "flagged":
        steps += card("👁️", "SENIOR LAWYER", routing.get("senior_name", "Senior"),
                      "⏳ Awaiting review — AI summary and flags delivered to inbox.",
                      is_ai=False, border_color="#d97706")

    # ── Status chip ───────────────────────────────────────────────────────
    SC = {
        "assigned": "#2563eb", "draft_submitted": "#d97706",
        "ai_reviewing": "#7c3aed", "flagged": "#dc2626",
        "accepted": "#16a34a", "completed": "#16a34a",
    }
    sc = SC.get(status, "#94a3b8")

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{
    background:#f8fafc;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    color:#1e293b;
    padding:16px 12px;
    overflow-x:hidden;
  }}
  @keyframes pulse{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
  @keyframes fadein{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
  .pipeline>*{{animation:fadein .25s ease-out both;}}
</style>
</head>
<body>
<div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid #e2e8f0;">
  <div>
    <div style="font-size:0.62rem;color:#94a3b8;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:2px;">Agent Pipeline</div>
    <div style="font-weight:700;font-size:0.95rem;color:#0f172a;">{matter['id']} — {matter.get('client','')}</div>
  </div>
  <div style="margin-left:auto;background:{sc}18;border:1px solid {sc}55;border-radius:20px;padding:3px 12px;font-size:0.72rem;color:{sc};font-weight:700;">
    {status.replace('_',' ').upper()}
  </div>
</div>
<div class="pipeline" style="display:flex;flex-direction:column;gap:6px;">
{steps}
</div>
</body>
</html>"""
