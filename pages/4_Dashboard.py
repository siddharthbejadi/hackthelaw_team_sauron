"""
Dashboard — firm-wide view + live agent pipeline monitor.
Every matter, every action labelled Human ✋ or AI 🤖.
Select any matter to see the full agent pipeline visualization.
"""
import streamlit as st
import streamlit.components.v1 as components
import requests
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from viz import build_matter_flow_html

API = "https://hackthelawteamsauron-production.up.railway.app"
st.set_page_config(page_title="Dashboard", layout="wide", page_icon="📊")

st.markdown("""
<style>
.stApp { background:#f8fafc; }
section[data-testid="stSidebar"] { background:#f1f5f9; }
.stApp, .stApp p, .stApp span, .stApp div, .stApp label,
.stApp .stMarkdown, .stApp .stText { color:#111 !important; }
.stApp h1, .stApp h2, .stApp h3 { color:#0f172a !important; }
.badge-ai    { background:#eff6ff; color:#2563eb; border-radius:4px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
.badge-human { background:#f0fdf4; color:#16a34a; border-radius:4px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
.metric-box  { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:14px; text-align:center; }
.metric-val  { font-size:2rem; font-weight:700; color:#0f172a; }
.metric-lbl  { font-size:0.72rem; color:#94a3b8; margin-top:3px; }
#MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard")
st.caption("Every matter · every action · every AI decision — fully transparent.")

col_h, col_r = st.columns([5, 1])
with col_r:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

matters = requests.get(f"{API}/matters").json()

if not matters:
    st.info("No matters yet. Submit one from the Partner view.")
    st.stop()

# ── Summary metrics ────────────────────────────────────────────────────────────
all_actions   = [a for m in matters for a in m.get("actions", [])]
ai_actions    = len([a for a in all_actions if a["actor_type"] == "ai"])
human_actions = len([a for a in all_actions if a["actor_type"] == "human"])
flagged       = len([m for m in matters if m["status"] == "flagged"])
completed     = len([m for m in matters if m["status"] in ("completed", "accepted")])
active        = len(matters) - completed

cols = st.columns(6)
for col, val, lbl, color in [
    (cols[0], len(matters),  "Total",        "#0f172a"),
    (cols[1], active,        "Active",        "#2563eb"),
    (cols[2], flagged,       "Flagged",       "#dc2626"),
    (cols[3], completed,     "Completed",     "#16a34a"),
    (cols[4], ai_actions,    "🤖 AI Actions", "#2563eb"),
    (cols[5], human_actions, "✋ Human",      "#16a34a"),
]:
    col.markdown(
        f'<div class="metric-box"><div class="metric-val" style="color:{color};">{val}</div>'
        f'<div class="metric-lbl">{lbl}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Two-panel layout: matter list (left) + pipeline viz (right) ───────────────
col_list, col_detail = st.columns([1, 3], gap="large")

with col_list:
    st.markdown("**Matters**")
    sf = st.selectbox("Filter", ["All", "flagged", "assigned", "accepted", "completed"], label_visibility="collapsed")
    filtered = matters if sf == "All" else [m for m in matters if m["status"] == sf]

    selected_id = st.session_state.get("dash_selected", filtered[0]["id"] if filtered else None)

    STATUS_COLOR = {
        "assigned": "#2563eb", "draft_submitted": "#d97706",
        "ai_reviewing": "#7c3aed", "flagged": "#dc2626",
        "accepted": "#16a34a", "completed": "#16a34a",
    }
    for m in filtered:
        sc = STATUS_COLOR.get(m["status"], "#888")
        ai_rev = m.get("ai_review") or {}
        is_sel = m["id"] == selected_id
        extra = f" · {ai_rev.get('overall_confidence','?')}% conf" if ai_rev else ""
        label = f"{'▶ ' if is_sel else ''}{m['id']} · {m['client'][:18]} · {m['status'].replace('_',' ').title()}{extra}"
        if st.button(
            label,
            key=f"dash_{m['id']}",
            use_container_width=True,
            type="primary" if is_sel else "secondary",
        ):
            st.session_state["dash_selected"] = m["id"]
            st.rerun()

with col_detail:
    selected = next((m for m in matters if m["id"] == selected_id), None)
    if not selected:
        st.info("Select a matter.")
        st.stop()

    ai_rev = selected.get("ai_review") or {}
    status = selected["status"]
    sc = STATUS_COLOR.get(status, "#888")

    # Top strip
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">'
        f'<div style="font-weight:700;font-size:1.1rem;color:#0f172a;">{selected["id"]} — {selected["client"]}</div>'
        f'<div style="background:{sc}18;border:1px solid {sc}88;border-radius:20px;padding:3px 12px;font-size:0.75rem;color:{sc};font-weight:700;">{status.replace("_"," ").upper()}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Metrics
    if ai_rev:
        p1, p2, p3, p4 = st.columns(4)
        conf = ai_rev.get("overall_confidence", "—")
        risk = ai_rev.get("overall_risk", "—")
        hf   = ai_rev.get("high_flag_count", 0)
        cit  = len(ai_rev.get("citations", []))
        conf_c = "#16a34a" if isinstance(conf,int) and conf>=70 else "#d97706" if isinstance(conf,int) and conf>=50 else "#dc2626"
        risk_c = "#dc2626" if isinstance(risk,int) and risk>60 else "#d97706" if isinstance(risk,int) and risk>30 else "#16a34a"
        for col, v, lbl, c in [(p1,f"{conf}%","Confidence",conf_c),(p2,f"{risk}%","Risk",risk_c),(p3,hf,"HIGH Flags","#dc2626" if hf else "#16a34a"),(p4,cit,"Citations","#2563eb")]:
            col.markdown(f'<div class="metric-box"><div class="metric-val" style="color:{c};font-size:1.4rem;">{v}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
        st.markdown("")

    # Tabs: Pipeline viz | Audit trail | Document
    tab_pipe, tab_audit, tab_doc = st.tabs(["🔍 Agent Pipeline", "📋 Audit Trail", "📄 Document"])

    with tab_pipe:
        html = build_matter_flow_html(selected)
        n = len(selected.get("actions", []))
        h = 500 + n * 18 + (280 if ai_rev else 0)
        components.html(html, height=min(h, 1300), scrolling=True)

    with tab_audit:
        actions = selected.get("actions", [])
        # Show last 5 actions; link to full audit for older ones
        show = actions[-5:] if len(actions) > 5 else actions
        if len(actions) > 5:
            st.caption(f"Showing last 5 of {len(actions)} actions.")
        for action in show:
            badge = '<span class="badge-ai">🤖 AI</span>' if action["actor_type"] == "ai" else '<span class="badge-human">✋ Human</span>'
            st.markdown(
                f"{badge} `{action['timestamp'][:16]}` **{action['role'].replace('_',' ').title()}** — {action['detail'][:80]}{'…' if len(action['detail'])>80 else ''}",
                unsafe_allow_html=True,
            )

    with tab_doc:
        draft = selected.get("draft")
        if draft:
            st.text_area("Draft", value=draft[:1200] + ("…\n[truncated — full draft below]" if len(draft) > 1200 else ""), height=300, disabled=True)
            if len(draft) > 1200:
                with st.expander("Show full draft"):
                    st.text(draft)
        else:
            st.info("No draft yet.")
        if ai_rev.get("citations"):
            st.caption("**AI citations:**")
            for c in ai_rev["citations"][:4]:
                st.markdown(f"[{c[:60]}](https://www.google.com/search?q={c.replace(' ','+')}+UK+law)")
            if len(ai_rev["citations"]) > 4:
                st.caption(f"+{len(ai_rev['citations'])-4} more — see Agent Pipeline tab")
