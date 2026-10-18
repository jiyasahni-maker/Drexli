# Drexli Demo Video — Recording Plan

**Target length:** 2 minutes 15 seconds to 2 minutes 45 seconds  
**Format:** One continuous screen recording with short narration; use the live app and real TinyFish responses.  
**Core message:** Drexli separates “Is this right for me?” from “What evidence supports this listing?”

## Before recording

- Start the app from the project directory: `streamlit run app.py`.
- Confirm `.env` contains your TinyFish API key. Never show `.env`, terminal environment output, or credentials on screen.
- Run `python -m pytest -q` and confirm the tests pass.
- Prepare one real opportunity listing from an identifiable organization with a source page and deadline. Copy the relevant details from the organization's public page; do not invent a deadline or application URL.
- Prepare two profile configurations to demonstrate that fit is personalized.
- Clear browser clutter and close tabs containing private information.
- If the network or TinyFish service fails, stop and retry rather than substituting fake results.

## Shot-by-shot storyboard and narration

### 0:00–0:12 — The problem
**On screen:** Drexli landing area.

**Narration:** “Finding opportunities is only half the problem. Students also need to know whether a listing is relevant to their goals and what evidence supports its claims. Drexli brings those two checks together.”

### 0:12–0:35 — Submit an opportunity
**On screen:** Paste the prepared real listing and click **Extract and verify**. Keep the profile sidebar visible briefly.

**Narration:** “I’ll paste an opportunity listing. Drexli extracts the details it can identify—such as the title, organization, type, deadline, and application URL. If a detail is missing, it should say so instead of making one up.”

### 0:35–1:10 — Live evidence review
**On screen:** Show the evidence status, claim-by-claim review, source links, and relevance labels. Open one source briefly if time permits.

**Narration:** “Drexli uses TinyFish Search to discover webpages and TinyFish Fetch to retrieve page content. It then checks whether sources appear relevant to the listing and reviews key claims individually. An unrelated official webpage does not count as corroboration, and ‘unverified’ does not automatically mean fraud.”

**Recording note:** Narrate only what the actual output supports. If the evidence is weak, describe that honestly; it demonstrates uncertainty handling rather than a failed demo.

### 1:10–1:35 — Personalized fit
**On screen:** Show the fit score and component breakdown. Change the profile preferences and rerun the same listing if time and API rate limits permit.

**Narration:** “Separately, Drexli calculates an explainable fit score from the available profile dimensions. The breakdown shows which interests and preferences contributed. This is a heuristic—not a probability of selection—and unknown information is not automatically treated as a mismatch.”

### 1:35–1:55 — Save and track
**On screen:** Click **Save opportunity**, then show it in the saved opportunities section and demonstrate a status update if stable.

**Narration:** “When I want to keep track of an opportunity, I can save it and update its application status. This helps turn a one-time check into a practical opportunity workflow.”

### 1:55–2:15 — Close with the differentiator
**On screen:** Return to the top of Drexli or show the final result summary.

**Narration:** “Drexli combines live web research, evidence-oriented review, and personalized matching. It doesn’t promise that every listing is safe. It helps users see what is supported, what remains uncertain, and whether the opportunity is worth their time.”

## Final recording checklist

- [ ] Use real results from the live TinyFish integration.
- [ ] Ensure source links are readable and relevant labels are visible.
- [ ] Show fit-score components, not only the headline number.
- [ ] Show the saved tracker only after successfully saving an item.
- [ ] Do not show API keys, `.env`, personal emails, or private data.
- [ ] Avoid saying “fraud detector,” “guaranteed safe,” or “100% accurate.”
- [ ] Keep the video concise, readable, and within the submission limit.
