"""
Partner View — submit client matters, track everything, see the full dashboard.
"""
import streamlit as st
import streamlit.components.v1 as components
import requests
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from viz import build_matter_flow_html

API = "https://hackthelawteamsauron-production.up.railway.app"
st.set_page_config(page_title="Partner View", layout="wide", page_icon="👔")

st.markdown("""
<style>
.stApp { background:#f8fafc; }
section[data-testid="stSidebar"] { background:#f1f5f9; }
.card { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:16px; margin-bottom:10px; }
.badge-ai    { background:#eff6ff; color:#2563eb; border-radius:4px; padding:2px 8px; font-size:0.75rem; font-weight:700; }
.badge-human { background:#f0fdf4; color:#16a34a; border-radius:4px; padding:2px 8px; font-size:0.75rem; font-weight:700; }
.status-pill { border-radius:20px; padding:3px 10px; font-size:0.78rem; font-weight:600; }
#MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

st.title("👔 Partner View")
st.caption("Submit client instructions and track all matters in your firm.")

tab_submit, tab_track = st.tabs(["📨 Submit New Matter", "📊 Track All Matters"])

# ---------------------------------------------------------------------------
# Tab 1 — Submit
# ---------------------------------------------------------------------------
with tab_submit:
    st.subheader("New Client Matter")

    col1, col2 = st.columns(2)
    with col1:
        client = st.text_input("Client name", placeholder="e.g. Nexus Technologies Ltd")
        partner_id = st.selectbox("Submitting as", ["partner_1", "partner_2"],
                                   format_func=lambda x: "Sarah Chen" if x == "partner_1" else "David Okafor")
    with col2:
        matter_type = st.selectbox("Matter type", [
            "Commercial Contract Review",
            "NDA Review",
            "Employment Contract",
            "IP Assignment",
            "Indemnity Clause Analysis",
            "Supplier Agreement",
        ])

    instructions = st.text_area(
        "Instructions to team",
        placeholder="e.g. Client has received a SaaS agreement from an NHS Trust. Review the indemnity and limitation of liability clauses. Flag any unlimited exposure. Redraft if necessary.",
        height=140,
    )

    if st.button("📨 Submit to AI Router", type="primary", use_container_width=True):
        if not client or not instructions:
            st.warning("Fill in client name and instructions.")
        else:
            with st.status("AI Router assigning matter to best available lawyer…", expanded=True) as status:
                resp = requests.post(f"{API}/matters/submit", json={
                    "client": client,
                    "instructions": instructions,
                    "partner_id": partner_id,
                    "matter_type": matter_type,
                })
                data = resp.json()
                routing = data.get("routing", {})
                status.update(label="✅ Matter assigned", state="complete")

            st.success(f"Matter **{data['matter_id']}** created and assigned.")

            st.markdown(f"""
            <div class="card">
                <div style="color:#94a3b8;font-size:0.75rem;margin-bottom:8px;letter-spacing:.5px;font-weight:600;">AI ROUTER DECISION</div>
                <b style="color:#1e293b">👤 Assigned to:</b> <span style="color:#16a34a">{routing.get('junior_name','—')}</span><br>
                <b style="color:#1e293b">👁️ Senior supervisor:</b> <span style="color:#2563eb">{routing.get('senior_name','—')}</span><br>
                <b style="color:#1e293b">📋 Matter type:</b> {routing.get('matter_type','—')}<br>
                <b style="color:#1e293b">💬 Instruction sent:</b> <span style="color:#475569">{routing.get('instruction_to_junior','—')[:200]}</span><br>
                <b style="color:#1e293b">🤖 Reasoning:</b> <span style="color:#64748b">{routing.get('reasoning','—')}</span>
            </div>
            """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tab 2 — Track
# ---------------------------------------------------------------------------
with tab_track:
    if st.button("🔄 Refresh", use_container_width=False):
        st.rerun()

    matters = requests.get(f"{API}/matters").json()

    if not matters:
        st.info("No matters yet. Submit one in the first tab.")
    else:
        STATUS_COLORS = {
            "submitted": "#94a3b8", "assigned": "#2563eb", "draft_submitted": "#d97706",
            "ai_reviewing": "#7c3aed", "flagged": "#dc2626", "senior_reviewing": "#d97706",
            "accepted": "#16a34a", "rejected": "#dc2626", "completed": "#16a34a",
        }

        for m in matters:
            color = STATUS_COLORS.get(m["status"], "#555")
            ai_review = m.get("ai_review") or {}
            conf = ai_review.get("overall_confidence", "—")
            risk = ai_review.get("overall_risk", "—")
            hf   = ai_review.get("high_flag_count", 0)

            with st.expander(
                f"{m['id']} — {m['client']} · {m['status'].replace('_',' ').title()} · "
                + (f"conf {conf}% · risk {risk}% · {hf} HIGH" if ai_review else m.get('matter_type','—')),
                expanded=False
            ):
                ca, cb, cc, cd = st.columns(4)
                ca.markdown(f"<span style='color:{color};font-weight:700'>{m['status'].replace('_',' ').title()}</span>", unsafe_allow_html=True)
                cb.markdown(f"**Junior:** `{m.get('assigned_to','—')}`")
                cc.markdown(f"**Senior:** `{m.get('senior_id','—')}`")
                cd.markdown(f"**Updated:** {m['updated_at'][:10]}")

                # Pipeline viz inside expander
                html = build_matter_flow_html(m)
                n_actions = len(m.get("actions", []))
                h = 420 + (n_actions * 16) + (220 if ai_review else 0)
                components.html(html, height=min(h, 900), scrolling=True)
