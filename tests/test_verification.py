from src.verification import verify_opportunity


class FakeClient:
    def __init__(self, search_results, pages):
        self.search_results = search_results
        self.pages = pages
        self.last_query = None

    def search(self, query, limit=5):
        self.last_query = query
        return self.search_results[:limit]

    def fetch(self, urls):
        return [self.pages[url] for url in urls if url in self.pages]


def test_unrelated_official_sources_are_not_corroboration():
    search_results = [
        {"title": "Deadlines & Timeline - Gilman Scholarship", "url": "https://www.gilmanscholarship.org/deadlines", "snippet": "Students can study and intern abroad."},
        {"title": "Know Your Dates and Deadlines - College Board", "url": "https://www.collegeboard.org/dates", "snippet": "Important dates and deadlines."},
    ]
    pages = {
        item["url"]: {"url": item["url"], "final_url": item["url"], "title": item["title"], "text": item["snippet"]}
        for item in search_results
    }
    client = FakeClient(search_results, pages)
    result = verify_opportunity(client, {
        "title": "Grand Internship Carnival", "organization": None, "type": "Internship",
        "deadline": "today", "application_url": None,
    }, "The application window for the Grand Internship Carnival closes today.")
    assert result["status"] == "Unverified — no relevant evidence found"
    assert result["relevant_source_count"] == 0
    assert all(not source["relevant"] for source in result["sources"])
    assert any(claim["status"] == "Missing information" for claim in result["claim_checks"])


def test_relevant_source_can_support_named_organization_and_deadline():
    url = "https://example.org/grand-internship-carnival"
    search_results = [{
        "title": "Grand Internship Carnival 2026 — Example Organization",
        "url": url,
        "snippet": "Example Organization confirms the Grand Internship Carnival closes 20 October 2026.",
    }]
    pages = {url: {
        "url": url, "final_url": url, "title": search_results[0]["title"],
        "text": "Example Organization confirms the Grand Internship Carnival. Applications close 20 October 2026.",
    }}
    client = FakeClient(search_results, pages)
    result = verify_opportunity(client, {
        "title": "Grand Internship Carnival", "organization": "Example Organization", "type": "Internship",
        "deadline": "20 October 2026", "application_url": url,
    }, "Grand Internship Carnival by Example Organization. Apply by 20 October 2026. https://example.org/grand-internship-carnival")
    assert result["relevant_source_count"] == 1
    assert result["status"] == "Relevant evidence found — review claims"
    assert all(claim["status"] == "Corroborated" for claim in result["claim_checks"])
    assert '"Grand Internship Carnival"' in client.last_query
