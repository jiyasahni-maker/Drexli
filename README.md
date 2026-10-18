# Drexli

**Discover boldly. Verify before you leap.**

Drexli is an AI-powered opportunity discovery and evidence-review prototype for jobs, internships, scholarships, research positions, fellowships, hackathons, and grants. The first MVP accepts pasted opportunity text, extracts basic fields, uses TinyFish Search and Fetch to retrieve live web evidence, produces an explainable preliminary fit assessment, and stores reviewed opportunities in SQLite.

## Current MVP status

This is a hackathon starter build. It uses conservative rule-based extraction and a transparent keyword heuristic for fit. It does not claim to prove that an opportunity is legitimate or fraudulent. “Unable to verify” means evidence was insufficient, not that the listing is a scam.

## Run locally

1. Install Python 3.11 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and add your TinyFish API key. Get a key at <https://agent.tinyfish.ai/api-keys>.
5. Start the app:

   ```bash
   streamlit run app.py
   ```

6. Run tests:

   ```bash
   pytest -q
   ```

## TinyFish integration

Drexli calls TinyFish Search (`https://api.search.tinyfish.ai`) to discover relevant pages and TinyFish Fetch (`https://api.fetch.tinyfish.ai`) to retrieve clean page content. Both requests use the `X-API-Key` header. Search and Fetch API details: <https://www.tinyfish.ai/free-search-fetch>.

## Security and limitations

- Never commit `.env`, API keys, personal data, or real inbox contents.
- Paste only information you are permitted to process; redact private data.
- A domain suffix alone is not proof of authenticity.
- The parser and fit score are heuristic baselines and can miss context, synonyms, eligibility rules, and date formats.
- Always independently visit the official organization's website before paying fees or submitting sensitive personal information.
- SQLite is local-only in this prototype; deployed ephemeral filesystems may not preserve saved data.

## Roadmap

- Improve structured extraction and date normalization.
- Compare specific claims against source text with claim-level citations.
- Add eligibility gates and a user profile.
- Add tests for false positives, missing evidence, and contradictory deadlines.
- Deploy and document a short live demo.

## Evidence review behavior

- Drexli scores source relevance using distinctive terms from the opportunity title and organization, and labels sources whose relevance is not established.
- Claim checks are shown separately for the organization, deadline, and application URL when those fields are present.
- Search results and a successful fetch are not, by themselves, evidence that a listing is legitimate.
- The current verification logic is a conservative heuristic, not a trained fraud detector. It may miss synonyms, alternate legal names, redirects, and date-format differences.

## TinyFish connection checks

The optional integration smoke checks are named `check_tinyfish_search.py` and `check_tinyfish_fetch.py` so pytest does not execute live API checks during normal test collection. Run them manually from the project directory after configuring `.env`:

```bash
python check_tinyfish_search.py
python check_tinyfish_fetch.py
```

The automated unit tests use mocked responses and do not require a live API key:

```bash
python -m pytest -q
```
