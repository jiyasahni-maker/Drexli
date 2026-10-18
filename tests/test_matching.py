from src.matching import assess_fit


def test_score_is_bounded_and_explained():
    result = assess_fit(
        {"title": "Python AI internship", "raw_text": "Python AI internship in India", "type": "Internship", "deadline": None, "organization": None},
        "Python, AI", ["Internship"], "India",
    )
    assert 0 <= result["score"] <= 100
    assert result["reasons"]
    assert result["components"]


def test_missing_profile_does_not_fake_a_50_percent_score():
    result = assess_fit(
        {"title": "Research assistant", "raw_text": "Research assistant position", "type": "Research"},
        "", [], "",
    )
    assert result["score"] is None
    assert result["confidence"] == "Not available"


def test_profile_changes_can_change_the_score():
    opportunity = {"title": "Python cybersecurity internship", "raw_text": "Python cybersecurity internship in India", "type": "Internship"}
    good_match = assess_fit(opportunity, "Python, cybersecurity", ["Internship"], "India")
    weak_match = assess_fit(opportunity, "biology, chemistry", ["Scholarship"], "Germany")
    assert good_match["score"] > weak_match["score"]


def test_unmentioned_location_is_unknown_not_a_penalty():
    result = assess_fit(
        {"title": "Python internship", "raw_text": "Python internship for students", "type": "Internship"},
        "Python", ["Internship"], "Germany",
    )
    assert "Location" not in result["components"]
    assert any("unknown" in reason.lower() for reason in result["reasons"])
