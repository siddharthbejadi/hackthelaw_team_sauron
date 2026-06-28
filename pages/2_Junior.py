"""
Junior Lawyer View
- All assigned matters with full context + agent pipeline viz
- Mode is auto-detected (no radio button):
    "Write my own draft"     → Manual  (just type and submit)
    "Generate AI draft"      → Hybrid  (AI starts, you edit)
    "Let AI handle it all"   → Autonomous (AI does everything, senior approves)
- Per-matter AI chat assistant scoped to each matter
"""
import streamlit as st
import streamlit.components.v1 as components
import requests
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from viz import build_matter_flow_html

API = "https://hackthelawteamsauron-production.up.railway.app"
st.set_page_config(page_title="Junior View", layout="wide", page_icon="📝")

st.markdown("""
<style>
.stApp { background:#f8fafc; }
section[data-testid="stSidebar"] { background:#f1f5f9; }
.card        { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:16px; margin-bottom:8px; }
.instr-card  { background:#f8fafc; border-left:3px solid #2563eb; border-radius:6px; padding:14px; color:#374151; font-size:0.88rem; line-height:1.6; }
.flag-high   { background:#fef2f2; border:1px solid #fca5a5; border-radius:6px; padding:5px 10px; margin:3px 0; font-size:0.8rem; color:#dc2626; }
.flag-med    { background:#fffbeb; border:1px solid #fcd34d; border-radius:6px; padding:5px 10px; margin:3px 0; font-size:0.8rem; color:#d97706; }
.rejected-banner { background:#fef2f2; border:1px solid #fca5a5; border-radius:8px; padding:14px; color:#dc2626; font-weight:700; margin-bottom:12px; }
.chat-msg-user { background:#eff6ff; border-radius:10px 10px 2px 10px; padding:10px 14px; margin:6px 0; color:#1e3a5f; font-size:0.85rem; text-align:right; }
.chat-msg-ai   { background:#fff; border:1px solid #e2e8f0; border-radius:10px 10px 10px 2px; padding:10px 14px; margin:6px 0; color:#374151; font-size:0.85rem; }
.badge-ai    { background:#eff6ff; color:#2563eb; border-radius:4px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
.badge-human { background:#f0fdf4; color:#16a34a; border-radius:4px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
#MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

st.title("📝 Junior Lawyer View")

JUNIOR_NAMES = {"junior_1": "Priya Patel", "junior_2": "Tom Davies", "junior_3": "Aisha Mensah"}
junior_id = st.sidebar.selectbox("Logged in as", list(JUNIOR_NAMES.keys()),
    format_func=lambda x: JUNIOR_NAMES[x])
st.sidebar.caption("Showing your assigned matters.")
if st.sidebar.button("🔄 Refresh"):
    st.rerun()

# ── Fetch matters ─────────────────────────────────────────────────────────────
all_matters = requests.get(f"{API}/matters").json()
my_matters  = [m for m in all_matters if m.get("assigned_to") == junior_id]
active      = [m for m in my_matters if m["status"] not in ("completed", "accepted")]
done        = [m for m in my_matters if m["status"] in ("completed", "accepted")]

st.markdown(f"**{len(active)} active** &nbsp;|&nbsp; **{len(done)} completed**")

if not active:
    st.info("No active matters assigned to you right now.")
    st.stop()

# ── One tab per active matter ─────────────────────────────────────────────────
tab_labels = [f"{m['id']} — {m['client']}" for m in active]
tabs = st.tabs(tab_labels)

for tab, matter in zip(tabs, active):
    with tab:
        status  = matter["status"]
        routing = matter.get("routing", {})
        mid     = matter["id"]

        # ── Status strip ──────────────────────────────────────────────────
        STATUS_COLORS = {
            "assigned": "#2563eb", "draft_submitted": "#d97706",
            "ai_reviewing": "#7c3aed", "flagged": "#dc2626",
            "accepted": "#16a34a", "completed": "#16a34a",
        }
        color = STATUS_COLORS.get(status, "#888")
        st.markdown(
            f'<div style="color:{color};font-weight:700;font-size:1rem;margin-bottom:4px;">'
            f'● {status.replace("_"," ").title()}</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"Matter type: {matter.get('matter_type','—')} | Last updated: {matter['updated_at'][:16]}")

        # ── Main two-column layout ─────────────────────────────────────────
        col_work, col_chat = st.columns([3, 2], gap="large")

        # ════════════════════════════════════════════════════════════════════
        # LEFT — Work area
        # ════════════════════════════════════════════════════════════════════
        with col_work:

            # Rejection banner
            if status == "draft_submitted":
                for action in reversed(matter.get("actions", [])):
                    if action["action"] == "rejected":
                        st.markdown(
                            f'<div class="rejected-banner">↩️ Your draft was rejected.<br>'
                            f'Reason: {action["detail"]}</div>',
                            unsafe_allow_html=True,
                        )
                        break

            # Instructions (truncated, expandable)
            instr = routing.get("instruction_to_junior") or matter.get("instructions", "")
            instr_short = instr[:200] + ("…" if len(instr) > 200 else "")
            st.markdown(f'<div class="instr-card">{instr_short}</div>', unsafe_allow_html=True)
            if len(instr) > 200:
                with st.expander("Full instructions"):
                    st.write(instr)

            # Previous AI flags after rejection (HIGH only, truncated)
            ai_review = matter.get("ai_review")
            if ai_review and status == "draft_submitted":
                high_fs = [f for f in ai_review.get("all_flags", []) if "HIGH" in str(f).upper()][:3]
                for f in high_fs:
                    st.markdown(f'<div class="flag-high">🔴 {str(f)[:90]}{"…" if len(str(f))>90 else ""}</div>', unsafe_allow_html=True)

            # AI review summary (collapsed, metrics only)
            if ai_review and status not in ("assigned", "draft_submitted"):
                with st.expander(f"🤖 AI Review · conf {ai_review.get('overall_confidence','?')}% · risk {ai_review.get('overall_risk','?')}% · {ai_review.get('high_flag_count',0)} HIGH"):
                    for f in ai_review.get("all_flags", [])[:4]:
                        fu = str(f).upper()
                        cls = "flag-high" if fu.startswith("HIGH") else "flag-med"
                        st.markdown(f'<div class="{cls}">{str(f)[:90]}</div>', unsafe_allow_html=True)
                    if len(ai_review.get("all_flags",[])) > 4:
                        st.caption(f"+{len(ai_review['all_flags'])-4} more flags — see Dashboard for full detail")
                    for c in ai_review.get("citations", [])[:3]:
                        st.markdown(f"[{c[:55]}](https://www.google.com/search?q={c.replace(' ','+')}+UK+law)")

            # Pipeline viz (collapsed)
            if matter.get("ai_review") or len(matter.get("actions", [])) > 2:
                with st.expander("🔍 Agent Pipeline"):
                    html = build_matter_flow_html(matter)
                    ai_rev = matter.get("ai_review") or {}
                    h = 380 + (len(matter.get("actions", [])) * 14) + (200 if ai_rev else 0)
                    components.html(html, height=min(h, 800), scrolling=True)

            # ── Work area: three action cards, auto-detect mode ───────────
            if status in ("assigned", "draft_submitted"):
                st.markdown("---")
                st.markdown("#### ✏️ How do you want to work on this?")

                chosen_mode = st.session_state.get(f"chosen_{mid}", None)

                c_manual, c_hybrid, c_auto_btn = st.columns(3)
                with c_manual:
                    st.markdown('<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:10px;text-align:center;"><div style="font-size:1.2rem;">✋</div><div style="color:#16a34a;font-weight:700;font-size:0.82rem;">Write my own</div><div style="color:#94a3b8;font-size:0.7rem;margin-top:3px;">AI reviews on submit.</div></div>', unsafe_allow_html=True)
                    if st.button("Select", key=f"pick_manual_{mid}", use_container_width=True, type="primary" if chosen_mode=="manual" else "secondary"):
                        st.session_state[f"chosen_{mid}"] = "manual"
                        st.rerun()
                with c_hybrid:
                    st.markdown('<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:10px;text-align:center;"><div style="font-size:1.2rem;">🤝</div><div style="color:#2563eb;font-weight:700;font-size:0.82rem;">AI starts, I edit</div><div style="color:#94a3b8;font-size:0.7rem;margin-top:3px;">AI drafts, you refine.</div></div>', unsafe_allow_html=True)
                    if st.button("Select", key=f"pick_hybrid_{mid}", use_container_width=True, type="primary" if chosen_mode=="hybrid" else "secondary"):
                        st.session_state[f"chosen_{mid}"] = "hybrid"
                        st.rerun()
                with c_auto_btn:
                    st.markdown('<div style="background:#faf5ff;border:1px solid #e9d5ff;border-radius:8px;padding:10px;text-align:center;"><div style="font-size:1.2rem;">🤖</div><div style="color:#9333ea;font-weight:700;font-size:0.82rem;">AI handles it all</div><div style="color:#94a3b8;font-size:0.7rem;margin-top:3px;">Senior approves output.</div></div>', unsafe_allow_html=True)
                    if st.button("Select", key=f"pick_auto_{mid}", use_container_width=True, type="primary" if chosen_mode=="autonomous" else "secondary"):
                        st.session_state[f"chosen_{mid}"] = "autonomous"
                        st.rerun()

                st.markdown("")
                mode_key = chosen_mode

                if mode_key is None:
                    st.info("☝️ Select how you want to work on this matter above.")

                # MANUAL
                elif mode_key == "manual":
                    draft = st.text_area(
                        "Your draft",
                        value=matter.get("draft", "") or "",
                        height=240,
                        placeholder="Write your legal draft here...",
                        key=f"draft_{mid}",
                    )
                    if st.button("📤 Submit to AI Supervisor", key=f"sub_{mid}", type="primary"):
                        if not draft.strip():
                            st.warning("Draft cannot be empty.")
                        else:
                            with st.status("AI Supervisor reviewing…", expanded=True) as s:
                                res = requests.post(f"{API}/matters/draft", json={
                                    "matter_id": mid, "junior_id": junior_id, "draft": draft,
                                }, timeout=300).json()
                                s.update(label="✅ Done" if res["status"] == "accepted" else "🚩 Flagged", state="complete")
                            if res["status"] == "accepted":
                                st.success("✅ AI Supervisor approved — no HIGH issues.")
                            else:
                                st.error("🚩 Flagged to senior lawyer.")
                                for f in res.get("ai_review", {}).get("all_flags", [])[:5]:
                                    fu = str(f).upper()
                                    st.markdown(f'<div class="{"flag-high" if fu.startswith("HIGH") else "flag-med"}">{f}</div>', unsafe_allow_html=True)
                            st.rerun()

                # HYBRID
                elif mode_key == "hybrid":  # noqa
                    if st.button("✨ Generate AI Draft", key=f"gen_{mid}", type="secondary"):
                        with st.status("AI drafting agent generating…", expanded=True) as s:
                            gen = requests.post(f"{API}/matters/generate_draft", json={
                                "matter_id": mid, "junior_id": junior_id,
                            }, timeout=300).json()
                            s.update(label="✅ AI draft ready — edit below", state="complete")
                        st.session_state[f"ai_draft_{mid}"] = gen.get("draft", "")
                        if gen.get("flags"):
                            for f in gen["flags"][:3]:
                                fu = str(f).upper()
                                st.markdown(f'<div class="{"flag-high" if fu.startswith("HIGH") else "flag-med"}">{f}</div>', unsafe_allow_html=True)

                    default = st.session_state.get(f"ai_draft_{mid}", matter.get("draft", "") or "")
                    draft = st.text_area(
                        "Edit the AI draft before submitting",
                        value=default, height=280,
                        placeholder="Click 'Generate AI Draft' first, then edit here...",
                        key=f"hybrid_{mid}",
                    )
                    if st.button("📤 Submit Edited Draft", key=f"hsub_{mid}", type="primary"):
                        if not draft.strip():
                            st.warning("Draft cannot be empty.")
                        else:
                            with st.status("AI Supervisor reviewing…", expanded=True) as s:
                                res = requests.post(f"{API}/matters/draft", json={
                                    "matter_id": mid, "junior_id": junior_id, "draft": draft,
                                }, timeout=300).json()
                                s.update(label="✅ Done" if res["status"] == "accepted" else "🚩 Flagged", state="complete")
                            if res["status"] == "accepted":
                                st.success("✅ Approved.")
                            else:
                                st.error("🚩 Flagged to senior.")
                                for f in res.get("ai_review", {}).get("all_flags", [])[:5]:
                                    fu = str(f).upper()
                                    st.markdown(f'<div class="{"flag-high" if fu.startswith("HIGH") else "flag-med"}">{f}</div>', unsafe_allow_html=True)
                            st.rerun()

                # AUTONOMOUS
                elif mode_key == "autonomous":
                    st.warning("⚠️ The AI will complete the entire matter. Output goes to senior for approval — you cannot edit it before then.")
                    if st.button("🚀 Run Fully Autonomous Pipeline", key=f"auto_{mid}", type="primary"):
                        with st.status("Research → Draft → Review → Risk Analysis running in parallel…", expanded=True) as s:
                            st.write("🔍 Research agent…")
                            st.write("✍️  Drafting agent…")
                            st.write("🔎 Review agent…")
                            st.write("⚠️  Risk analysis agent…")
                            res = requests.post(f"{API}/matters/autonomous", json={
                                "matter_id": mid, "junior_id": junior_id,
                            }, timeout=600).json()
                            s.update(label="✅ Pipeline complete — awaiting senior approval", state="complete")
                        st.success("🤖 AI completed the full pipeline. Sent to senior for approval.")
                        ai_rev = res.get("ai_review", {})
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Confidence", f"{ai_rev.get('overall_confidence','?')}%")
                        c2.metric("Risk",        f"{ai_rev.get('overall_risk','?')}%")
                        c3.metric("HIGH Flags",   ai_rev.get("high_flag_count", 0))
                        for f in ai_rev.get("all_flags", [])[:6]:
                            fu = str(f).upper()
                            st.markdown(f'<div class="{"flag-high" if fu.startswith("HIGH") else "flag-med"}">{f}</div>', unsafe_allow_html=True)
                        st.rerun()

            elif status == "flagged":
                st.warning("🚩 Flagged to senior lawyer. Awaiting their decision.")
            elif status == "ai_reviewing":
                st.info("🤖 AI pipeline is running…")

        # ════════════════════════════════════════════════════════════════════
        # RIGHT — Per-matter AI chat assistant
        # ════════════════════════════════════════════════════════════════════
        with col_chat:
            st.markdown("#### 🤖 AI Legal Assistant")
            st.caption("Ask anything about this matter — research, clause drafting, risk questions. The AI has full context of your instructions.")

            chat_key = f"chat_{mid}"
            if chat_key not in st.session_state:
                st.session_state[chat_key] = []

            # Display chat history
            chat_container = st.container(height=420)
            with chat_container:
                if not st.session_state[chat_key]:
                    st.markdown(
                        '<div style="color:#555;font-size:0.82rem;text-align:center;margin-top:40px;">'
                        'Ask me anything about this matter.<br><br>'
                        '<b style="color:#333">Try:</b><br>'
                        '"What does UCTA 1977 say about unlimited indemnity?"<br>'
                        '"Draft a mutual liability cap clause at £240k"<br>'
                        '"What are the key risks here?"</div>',
                        unsafe_allow_html=True,
                    )
                for msg in st.session_state[chat_key]:
                    if msg["role"] == "user":
                        st.markdown(f'<div class="chat-msg-user">✋ {msg["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-msg-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

            # Chat input
            user_msg = st.chat_input("Ask about this matter…", key=f"chat_input_{mid}")
            if user_msg:
                st.session_state[chat_key].append({"role": "user", "content": user_msg})
                with st.spinner("AI thinking…"):
                    resp = requests.post(f"{API}/matters/chat", json={
                        "matter_id": mid,
                        "junior_id": junior_id,
                        "message": user_msg,
                        "history": st.session_state[chat_key][:-1],
                    }, timeout=180).json()
                ai_reply = resp.get("response", "Sorry, I couldn't get a response.")
                st.session_state[chat_key].append({"role": "assistant", "content": ai_reply})
                st.rerun()

            # Clear chat
            if st.session_state[chat_key]:
                if st.button("🗑️ Clear chat", key=f"clear_{mid}", use_container_width=True):
                    st.session_state[chat_key] = []
                    st.rerun()
