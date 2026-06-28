"""
Senior Lawyer View — review flagged matters, see AI summary, approve or reject.
"""
import streamlit as st
import requests

API = "https://hackthelawteamsauron-production.up.railway.app"
st.set_page_config(page_title="Senior View", layout="wide", page_icon="👁️")

st.markdown("""
<style>
.stApp { background:#f8fafc; }
section[data-testid="stSidebar"] { background:#f1f5f9; }
.card  { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:16px; margin-bottom:10px; }
.flag-high { background:#fef2f2; border:1px solid #fca5a5; border-radius:6px; padding:6px 12px; margin:4px 0; font-size:0.82rem; color:#dc2626; }
.flag-med  { background:#fffbeb; border:1px solid #fcd34d; border-radius:6px; padding:6px 12px; margin:4px 0; font-size:0.82rem; color:#d97706; }
.flag-low  { background:#eff6ff; border:1px solid #bfdbfe; border-radius:6px; padding:6px 12px; margin:4px 0; font-size:0.82rem; color:#2563eb; }
.metric-box { background:#fff; border:1px solid #e2e8f0; border-radius:8px; padding:12px; text-align:center; }
.metric-val { font-size:1.6rem; font-weight:700; color:#0f172a; }
.metric-lbl { font-size:0.72rem; color:#94a3b8; margin-top:2px; }
.badge-ai    { background:#eff6ff; color:#2563eb; border-radius:4px; padding:2px 8px; font-size:0.75rem; font-weight:700; }
.badge-human { background:#f0fdf4; color:#16a34a; border-radius:4px; padding:2px 8px; font-size:0.75rem; font-weight:700; }
#MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

st.title("👁️ Senior Lawyer Review")

senior_id = st.sidebar.selectbox("Logged in as", ["senior_1", "senior_2"],
    format_func=lambda x: "James Wright" if x == "senior_1" else "Meera Nair")

if st.sidebar.button("🔄 Refresh"):
    st.rerun()

# Fetch flagged matters assigned to this senior
all_matters = requests.get(f"{API}/matters").json()
flagged = [m for m in all_matters if m.get("senior_id") == senior_id and m["status"] == "flagged"]
completed = [m for m in all_matters if m.get("senior_id") == senior_id and m["status"] in ("completed","accepted")]

st.markdown(f"**{len(flagged)} flagged for your review** &nbsp;|&nbsp; **{len(completed)} completed**")

if not flagged:
    st.success("✅ No matters flagged for your review right now.")
else:
    st.markdown("---")

for matter in flagged:
    ai_review = matter.get("ai_review") or {}
    review_data    = ai_review.get("review", {})
    risk_data      = ai_review.get("risk_analysis", {})
    all_flags      = ai_review.get("all_flags", [])
    citations      = ai_review.get("citations", [])
    overall_conf   = ai_review.get("overall_confidence", 0)
    overall_risk   = ai_review.get("overall_risk", 0)
    high_flag_count = ai_review.get("high_flag_count", 0)

    st.markdown(f"### Matter {matter['id']} — {matter['client']}")
    st.caption(f"{matter.get('matter_type','—')} | Last updated: {matter['updated_at'][:16]}")

    # Top metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f'<div class="metric-box"><div class="metric-val">{overall_conf}%</div><div class="metric-lbl">AI Confidence</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-box"><div class="metric-val">{overall_risk}%</div><div class="metric-lbl">Matter Risk</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-box"><div class="metric-val">{high_flag_count}</div><div class="metric-lbl">HIGH Flags</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-box"><div class="metric-val">{len(citations)}</div><div class="metric-lbl">Citations</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        # AI flags summary
        st.markdown("**⚠️ AI Flags — issues found in the draft**")
        for f in all_flags:
            fu = str(f).upper()
            if fu.startswith("HIGH"):
                st.markdown(f'<div class="flag-high">🔴 {f}</div>', unsafe_allow_html=True)
            elif fu.startswith("MEDIUM"):
                st.markdown(f'<div class="flag-med">🟡 {f}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="flag-low">🔵 {f}</div>', unsafe_allow_html=True)

        # Citations
        if citations:
            st.markdown("**📚 Citations verified by AI**")
            for c in citations[:6]:
                query = c.replace(" ", "+")
                st.markdown(f'- [{c}](https://www.google.com/search?q={query}+case+law+UK)')

    with col_right:
        # AI review output
        st.markdown("**AI Review Summary**")
        preview = str(review_data.get("output",""))[:300]
        rest    = str(review_data.get("output",""))[300:]
        st.markdown(f'<div class="card" style="font-size:0.85rem;color:#374151;">{preview}{"…" if rest else ""}</div>', unsafe_allow_html=True)
        if rest:
            with st.expander("Full AI review"):
                st.write(review_data.get("output",""))

        # Full document link
        st.markdown(f"🔗 [View junior's full draft]({matter.get('document_url','#')})")

    # Audit trail — last 4 actions only
    with st.expander("📋 Audit Trail"):
        acts = matter.get("actions", [])
        for action in acts[-4:]:
            badge = '<span class="badge-ai">🤖 AI</span>' if action["actor_type"]=="ai" else '<span class="badge-human">✋ Human</span>'
            st.markdown(f"{badge} `{action['timestamp'][:16]}` **{action['role'].replace('_',' ').title()}** — {action['detail'][:70]}{'…' if len(action['detail'])>70 else ''}", unsafe_allow_html=True)
        if len(acts) > 4:
            st.caption(f"Full audit ({len(acts)} entries) available in Dashboard.")

    # Decision
    st.markdown("---")
    st.markdown("**Your Decision**")
    notes = st.text_area("Notes / reason for decision", key=f"notes_{matter['id']}",
                          placeholder="e.g. Approved — clause redrafted correctly. / Rejected — indemnity cap still missing.")

    col_acc, col_rej = st.columns(2)
    with col_acc:
        if st.button("✅ Accept & Complete", key=f"acc_{matter['id']}", type="primary", use_container_width=True):
            requests.post(f"{API}/matters/decision", json={
                "matter_id": matter["id"],
                "senior_id": senior_id,
                "decision": "accepted",
                "notes": notes,
            })
            st.success("Matter accepted and completed.")
            st.rerun()

    with col_rej:
        if st.button("↩️ Reject — Return to Junior", key=f"rej_{matter['id']}", use_container_width=True):
            if not notes.strip():
                st.warning("Please add a reason before rejecting.")
            else:
                requests.post(f"{API}/matters/decision", json={
                    "matter_id": matter["id"],
                    "senior_id": senior_id,
                    "decision": "rejected",
                    "notes": notes,
                })
                st.error("Matter rejected and returned to junior with your feedback.")
                st.rerun()

    st.markdown("---")
