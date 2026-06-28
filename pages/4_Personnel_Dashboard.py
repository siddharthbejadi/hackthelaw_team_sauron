"""
Personnel Dashboard — individual lawyer's personal workload view.
Shows only matters assigned to the logged-in lawyer.
"""
import streamlit as st
import requests

API = "https://hackthelawteamsauron-production.up.railway.app"
st.set_page_config(page_title="Personnel Dashboard", layout="wide", page_icon="👤")

st.markdown("""
<style>
.stApp { background:#f8fafc; }
section[data-testid="stSidebar"] { background:#f1f5f9; }
.metric-box  { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:14px; text-align:center; }
.metric-val  { font-size:2rem; font-weight:700; color:#0f172a; }
.metric-lbl  { font-size:0.72rem; color:#94a3b8; margin-top:3px; }
.badge-ai    { background:#eff6ff; color:#2563eb; border-radius:4px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
.badge-human { background:#f0fdf4; color:#16a34a; border-radius:4px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
.flag-high { background:#fef2f2; border:1px solid #fca5a5; border-radius:6px; padding:6px 12px; margin:4px 0; font-size:0.82rem; color:#dc2626; }
.flag-med  { background:#fffbeb; border:1px solid #fcd34d; border-radius:6px; padding:6px 12px; margin:4px 0; font-size:0.82rem; color:#d97706; }
.flag-low  { background:#eff6ff; border:1px solid #bfdbfe; border-radius:6px; padding:6px 12px; margin:4px 0; font-size:0.82rem; color:#2563eb; }
#MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

st.title("👤 Personnel Dashboard")
st.caption("Your personal workload — matters assigned to you, actions required.")

# Lawyer selector
LAWYERS = {
    "junior_1": "Alice Mensah (Junior)",
    "junior_2": "Tom Bradley (Junior)",
    "senior_1": "James Wright (Senior)",
    "senior_2": "Meera Nair (Senior)",
}
lawyer_id = st.sidebar.selectbox(
    "Logged in as",
    list(LAWYERS.keys()),
    format_func=lambda x: LAWYERS[x]
)

if st.sidebar.button("🔄 Refresh"):
    st.rerun()

try:
    all_matters = requests.get(f"{API}/matters", timeout=8).json()
except Exception as e:
    st.error(f"Could not reach backend: {e}")
    st.stop()

# Filter to this lawyer's matters only
my_matters = [
    m for m in all_matters
    if m.get("assigned_to") == lawyer_id or m.get("senior_id") == lawyer_id
]

if not my_matters:
    st.info(f"No matters currently assigned to {LAWYERS[lawyer_id]}.")
    st.stop()

# Personal metrics
total          = len(my_matters)
active         = len([m for m in my_matters if m["status"] not in ("completed", "accepted")])
completed_cnt  = len([m for m in my_matters if m["status"] in ("completed", "accepted")])
flagged        = len([m for m in my_matters if m["status"] == "flagged"])
pending_action = len([m for m in my_matters if m["status"] in ("draft_submitted", "flagged", "assigned")])

cols = st.columns(5)
for col, val, lbl, color in [
    (cols[0], total,          "My Matters",      "#0f172a"),
    (cols[1], active,         "Active",           "#2563eb"),
    (cols[2], pending_action, "Action Required",  "#d97706"),
    (cols[3], flagged,        "Flagged",          "#dc2626"),
    (cols[4], completed_cnt,  "Completed",        "#16a34a"),
]:
    col.markdown(
        f'<div class="metric-box"><div class="metric-val" style="color:{color};">{val}</div>'
        f'<div class="metric-lbl">{lbl}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

STATUS_COLOR = {
    "assigned": "#2563eb", "draft_submitted": "#d97706",
    "ai_reviewing": "#7c3aed", "flagged": "#dc2626",
    "accepted": "#16a34a", "completed": "#16a34a",
}

ACTION_NEEDED = {
    "assigned":        "✍️ Draft required",
    "draft_submitted": "⏳ Awaiting AI review",
    "ai_reviewing":    "⏳ AI reviewing",
    "flagged":         "🔴 Senior review needed",
    "accepted":        "✅ Completed",
    "completed":       "✅ Completed",
}

# Sort: action-required matters first
my_matters_sorted = sorted(
    my_matters,
    key=lambda m: 0 if m["status"] in ("assigned", "flagged") else 1
)

for m in my_matters_sorted:
    ai_rev = m.get("ai_review") or {}
    status = m["status"]
    sc = STATUS_COLOR.get(status, "#888")
    action_label = ACTION_NEEDED.get(status, status.replace("_", " ").title())
    role_label = "Junior (you)" if m.get("assigned_to") == lawyer_id else "Senior Supervisor (you)"
    conf = ai_rev.get("overall_confidence", "—")
    risk = ai_rev.get("overall_risk", "—")

    with st.expander(
        f"{m['id']} — {m['client']} · {action_label}",
        expanded=(status in ("assigned", "flagged"))
    ):
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**Role:** {role_label}")
        c2.markdown(f"**Matter type:** {m.get('matter_type', '—')}")
        c3.markdown(
            f"**Status:** <span style='color:{sc};font-weight:700'>{status.replace('_',' ').title()}</span>",
            unsafe_allow_html=True
        )

        if ai_rev:
            st.markdown("---")
            a1, a2, a3 = st.columns(3)
            conf_c = "#16a34a" if isinstance(conf,int) and conf>=70 else "#d97706" if isinstance(conf,int) and conf>=50 else "#dc2626"
            risk_c = "#dc2626" if isinstance(risk,int) and risk>60 else "#d97706" if isinstance(risk,int) and risk>30 else "#16a34a"
            a1.markdown(f'<div class="metric-box"><div class="metric-val" style="color:{conf_c};font-size:1.3rem;">{conf}%</div><div class="metric-lbl">AI Confidence</div></div>', unsafe_allow_html=True)
            a2.markdown(f'<div class="metric-box"><div class="metric-val" style="color:{risk_c};font-size:1.3rem;">{risk}%</div><div class="metric-lbl">Risk Score</div></div>', unsafe_allow_html=True)
            a3.markdown(f'<div class="metric-box"><div class="metric-val" style="color:#dc2626;font-size:1.3rem;">{ai_rev.get("high_flag_count",0)}</div><div class="metric-lbl">HIGH Flags</div></div>', unsafe_allow_html=True)

            flags = ai_rev.get("all_flags", [])
            if flags:
                st.markdown("**⚠️ AI Flags on your work:**")
                for f in flags[:5]:
                    fu = str(f).upper()
                    if fu.startswith("HIGH"):
                        st.markdown(f'<div class="flag-high">🔴 {f}</div>', unsafe_allow_html=True)
                    elif fu.startswith("MEDIUM"):
                        st.markdown(f'<div class="flag-med">🟡 {f}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="flag-low">🔵 {f}</div>', unsafe_allow_html=True)

        if m.get("instructions"):
            st.markdown("**📋 Instructions from Partner:**")
            st.info(m["instructions"][:400] + ("…" if len(m.get("instructions", "")) > 400 else ""))

        if m.get("draft"):
            with st.expander("📄 View your draft"):
                st.text(m["draft"][:1000] + ("…" if len(m.get("draft", "")) > 1000 else ""))

        acts = m.get("actions", [])
        if acts:
            last = acts[-1]
            badge = '<span class="badge-ai">🤖 AI</span>' if last["actor_type"] == "ai" else '<span class="badge-human">✋ Human</span>'
            st.caption(f"Last action: {badge} `{last['timestamp'][:16]}` — {last['detail'][:80]}", unsafe_allow_html=True)
