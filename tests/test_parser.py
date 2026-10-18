from src.email_parser import extract_opportunity

def test_extracts_url_deadline_and_type():
    text = "AI Research Internship\nApply by 20 October 2026\nApply: https://example.org/apply"
    result = extract_opportunity(text)
    assert result["application_url"] == "https://example.org/apply"
    assert result["type"] == "Internship"
    assert result["deadline"] is not None
    assert "example.org" in result["domains"]

def test_cleans_title_and_extracts_today_deadline():
    result = extract_opportunity("The application window for the Grand Internship Carnival closes today.")
    assert result["title"] == "Grand Internship Carnival"
    assert result["deadline"].lower() == "today"
