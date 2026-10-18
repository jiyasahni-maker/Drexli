import streamlit as st
from src.email_parser import extract_opportunity
from src.tinyfish_client import TinyFishClient, TinyFishError
from src.verification import verify_opportunity
from src.matching import assess_fit
from src.database import init_db, save_opportunity, list_opportunities, update_status

st.set_page_config(page_title="Drexli | Discover boldly", page_icon="🧭", layout="wide")
init_db()

st.title("🧭 Drexli")
st.caption("Discover boldly. Verify before you leap.")
st.write("Find opportunities worth your time — and inspect the evidence before you trust a listing.")

with st.sidebar:
    st.header("Your profile")
    interests = st.text_input("Skills / interests", placeholder="Python, AI/ML, cybersecurity")
    preferred_types = st.multiselect("Opportunity types", ["Job", "Internship", "Scholarship", "Research", "Fellowship", "Hackathon", "Grant"], default=["Internship", "Research", "Hackathon"])
    location = st.text_input("Preferred location", placeholder="India / Remote / Germany")
    st.divider()
    st.caption("Drexli provides evidence signals, not a guarantee that an opportunity is legitimate.")

st.subheader("Check an opportunity")
raw_text = st.text_area("Paste an opportunity email or listing", height=220, placeholder="Paste the full message or opportunity description here…")
if st.button("Extract and verify", type="primary", use_container_width=True, disabled=not raw_text.strip()):
    opportunity = extract_opportunity(raw_text)
    st.session_state["opportunity"] = opportunity
    st.session_state["raw_text"] = raw_text
    with st.spinner("Searching the live web and checking source evidence with TinyFish…"):
        try:
            client = TinyFishClient()
            verification = verify_opportunity(client, opportunity, raw_text)
            st.session_state["verification"] = verification
            st.session_state["api_error"] = None
        except TinyFishError as exc:
            st.session_state["verification"] = None
            st.session_state["api_error"] = str(exc)

if "opportunity" in st.session_state:
    opp = st.session_state["opportunity"]
    st.subheader("Extracted details")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Opportunity**", opp.get("title") or "Not identified")
        st.write("**Organization**", opp.get("organization") or "Not identified")
        st.write("**Type**", opp.get("type") or "Not identified")
    with c2:
        st.write("**Deadline**", opp.get("deadline") or "Not identified")
        st.write("**Application URL**", opp.get("application_url") or "Not identified")
        st.write("**Email domains / URLs**", ", ".join(opp.get("domains", [])) or "None detected")

    err = st.session_state.get("api_error")
    verification = st.session_state.get("verification")
    if err:
        st.error(f"TinyFish verification did not complete: {err}")
        st.info("Check your TINYFISH_API_KEY in .env, then try again. Drexli will not invent verification results.")
    elif verification:
        st.subheader("Evidence review")
        st.caption(f"Checked at: {verification['checked_at']} · Live TinyFish Search + Fetch")
        st.write(f"**Evidence status: {verification['status']}**")
        if verification["status"].startswith("Unverified") or "unconfirmed" in verification["status"].lower():
            st.warning(verification["status"])
        else:
            st.write(f"**{verification['status']}**")
        st.write(verification["summary"])
        if verification.get("claim_checks"):
            st.markdown("**Claim-by-claim review**")
            for claim in verification["claim_checks"]:
                status = claim["status"]
                if status == "Corroborated":
                    st.success(f"{status}: {claim['claim']} — {claim['explanation']}")
                elif status == "Conflicting evidence":
                    st.error(f"{status}: {claim['claim']} — {claim['explanation']}")
                else:
                    st.warning(f"{status}: {claim['claim']} — {claim['explanation']}")
        if verification["signals"]:
            st.markdown("**Assessment notes**")
            for signal in verification["signals"]:
                st.write(f"- {signal}")
        st.markdown("**Sources reviewed**")
        sources = sorted(verification["sources"], key=lambda item: (not item.get("relevant", False), -item.get("relevance_score", 0)))
        for source in sources:
            relevance = "Relevant to listing" if source.get("relevant") else "Relevance not established"
            st.markdown(f"- [{source['title'] or source['url']}]({source['url']}) — **{relevance}** · {source.get('source_type', 'Source')} · {source.get('relevance_reason', '')}")
            if source.get("snippet"):
                st.caption(source["snippet"][:300])
        st.caption("‘Unverified’ means Drexli could not find enough supporting evidence; it does not by itself mean fraud. A relevant source is not automatically authentic.")

    st.subheader("Personalized fit")
    fit = assess_fit(opp, interests, preferred_types, location)
    if fit["score"] is None:
        st.info("Not enough profile information to calculate a personalized fit score. Add skills/interests and select opportunity types in the sidebar.")
    else:
        st.metric("Indicative fit", f"{fit['score']}/100")
        st.caption(f"Profile coverage: {fit['confidence']} · Heuristic score, not a probability of success.")
        if fit.get("components"):
            st.markdown("**Score breakdown**")
            for component, details in fit["components"].items():
                st.write(f"- **{component}: {details['score']}/100** (weight {round(details['weight'] * 100)}% before normalization)")
    for reason in fit["reasons"]:
        st.write(f"- {reason}")
    st.caption("This transparent heuristic is not a validated prediction. Unknown information is excluded from the score rather than treated as a mismatch.")

    if st.button("Save opportunity", disabled=not verification):
        save_opportunity(opp, verification, fit)
        st.success("Saved to your Drexli tracker.")

st.divider()
st.subheader("Saved opportunities")
items = list_opportunities()
if not items:
    st.caption("Nothing saved yet. Verify an opportunity above to start your tracker.")
else:
    for item in items:
        with st.expander(f"{item['title'] or 'Untitled opportunity'} · {item['organization'] or 'Unknown organization'}"):
            saved_fit = f"{item['fit_score']}/100" if item['fit_score'] is not None else "Not assessed"
            st.write(f"Status: **{item['status']}** · Evidence: **{item['evidence_status']}** · Fit: **{saved_fit}**")
            st.write(f"Deadline: {item['deadline'] or 'Not identified'}")
            if item['application_url']:
                st.markdown(f"[Open application]({item['application_url']})")
            new_status = st.selectbox("Update status", ["Saved", "Planning to apply", "Applied", "Rejected", "Accepted", "Expired"], index=["Saved", "Planning to apply", "Applied", "Rejected", "Accepted", "Expired"].index(item['status']), key=f"status_{item['id']}")
            if st.button("Update", key=f"update_{item['id']}"):
                update_status(item['id'], new_status)
                st.rerun()
