# Drexli Prototype Stabilization Patch

## What changed

- Improved opportunity title cleanup for common announcement phrasing such as “The application window for the Grand Internship Carnival closes today.”
- Added relevance assessment for TinyFish results so unrelated pages are not treated as supporting evidence merely because they exist or use a recognized domain.
- Added claim-by-claim checks for organization, deadline, and application URL when those fields are available.
- Added source relevance labels and claim review to the Streamlit interface.
- Renamed live API smoke-check scripts so pytest does not execute them automatically during test collection.
- Added mocked tests for irrelevant sources and relevant supporting evidence.
- Added `.env.example` because the README referenced it but it was missing from the uploaded project.
- Added `DEMO_VIDEO_SCRIPT.md` with a practical 2–3 minute recording plan.
- Changed the fit-score UI label from “Assessment confidence” to “Profile coverage” to avoid suggesting confidence in the opportunity's legitimacy.

## Test results

The patched project passed: `python -m pytest -q` — **8 passed**.

Python syntax compilation passed for the app, source modules, and TinyFish smoke-check scripts.

## Install safely on macOS

1. Keep your current project as a backup.
2. Extract the new `drexli` folder somewhere separate.
3. Copy your existing local `.env` into the new folder (never share or commit it).
4. If you need to preserve saved tracker entries, copy your existing `drexli.db` into the new folder. Otherwise, the app creates a fresh database on startup.
5. Open Terminal in the new project folder and activate your existing compatible virtual environment or create a new one.
6. Install dependencies and run tests:

   ```bash
   python -m pip install -r requirements.txt
   python -m pytest -q
   ```

7. Launch the app:

   ```bash
   python -m streamlit run app.py
   ```

8. For live TinyFish checks, run the renamed scripts manually only after `.env` is configured:

   ```bash
   python check_tinyfish_search.py
   python check_tinyfish_fetch.py
   ```

## Limitations to disclose

- Verification and source relevance are heuristic baselines, not a trained fraud detector.
- Claim matching may miss synonyms, alternate organization names, date-format differences, and complex redirects.
- A relevant source is not automatically authentic, and a missing result does not prove fraud.
- SQLite is local-file persistence; a hosted environment may require a persistent volume or external database.
