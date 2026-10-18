"""Transparent, profile-aware opportunity fit scoring.

This is an explainable heuristic, not a validated prediction model.
Unknown dimensions are omitted from the weighted average rather than scored as zero.
"""
import re

WEIGHTS = {
    "interests": 0.60,
    "opportunity_type": 0.25,
    "location": 0.15,
}


def _normalise(value):
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def _contains_term(text, term):
    """Match a phrase/token without accidental substring matches (e.g. AI in said)."""
    term = _normalise(term)
    if not term:
        return False
    if " " in term:
        return term in text
    return re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text) is not None


def assess_fit(opportunity, interests, preferred_types, location):
    """Return a normalized fit score, component breakdown, confidence, and reasons.

    Score dimensions:
      * listed interests / skills: 60% weight
      * preferred opportunity type: 25% weight
      * preferred location: 15% weight, only when the listing explicitly mentions it

    Weights are renormalized across dimensions that can actually be assessed. A missing
    profile or unmentioned location is treated as unknown, not as a negative match.
    """
    title = _normalise(opportunity.get("title"))
    raw_text = _normalise(opportunity.get("raw_text"))
    searchable_text = f"{title} {raw_text}".strip()
    reasons = []
    components = {}
    available_weight = 0.0
    weighted_total = 0.0

    interest_list = [item.strip() for item in (interests or "").split(",") if item.strip()]
    if interest_list and searchable_text:
        matched = [item for item in interest_list if _contains_term(searchable_text, item)]
        component_score = round(100 * len(matched) / len(interest_list))
        components["Interests and skills"] = {
            "score": component_score,
            "weight": WEIGHTS["interests"],
            "matched": matched,
            "considered": interest_list,
        }
        available_weight += WEIGHTS["interests"]
        weighted_total += component_score * WEIGHTS["interests"]
        if matched:
            reasons.append(f"Interest overlap: {', '.join(matched)} ({len(matched)} of {len(interest_list)} listed interests matched).")
        else:
            reasons.append("None of your listed interests matched the title or pasted description. Exact keyword matching may miss synonyms.")
    else:
        reasons.append("Interest match is unavailable. Add comma-separated skills or interests to personalize this assessment.")

    preferred = { _normalise(item) for item in (preferred_types or []) if _normalise(item) }
    opp_type = _normalise(opportunity.get("type"))
    if preferred and opp_type:
        component_score = 100 if opp_type in preferred else 0
        components["Opportunity type"] = {
            "score": component_score,
            "weight": WEIGHTS["opportunity_type"],
            "detected": opportunity.get("type"),
            "preferred": sorted(preferred),
        }
        available_weight += WEIGHTS["opportunity_type"]
        weighted_total += component_score * WEIGHTS["opportunity_type"]
        if component_score:
            reasons.append(f"Opportunity type matches your preference: {opportunity.get('type')}.")
        else:
            reasons.append(f"Detected type ({opportunity.get('type')}) is not among your selected opportunity types.")
    else:
        reasons.append("Opportunity-type match is unavailable because the type or your preferences are missing.")

    preferred_location = _normalise(location)
    if preferred_location:
        # A location contributes only when the listing explicitly names it. Absence is unknown.
        if _contains_term(searchable_text, preferred_location):
            components["Location"] = {
                "score": 100,
                "weight": WEIGHTS["location"],
                "preferred": location.strip(),
            }
            available_weight += WEIGHTS["location"]
            weighted_total += 100 * WEIGHTS["location"]
            reasons.append(f"Preferred location ({location.strip()}) appears in the listing.")
        else:
            reasons.append(f"Location match is unknown: the listing does not explicitly mention {location.strip()!r}. This was not scored as a mismatch.")
    else:
        reasons.append("No preferred location provided; location was not included in the score.")

    if available_weight == 0:
        score = None
        confidence = "Not available"
        reasons.insert(0, "Not enough profile or listing information to calculate a personalized score. Add interests and select opportunity types.")
    else:
        score = round(weighted_total / available_weight)
        coverage = available_weight / sum(WEIGHTS.values())
        confidence = "High coverage" if coverage >= 0.80 else "Medium coverage" if coverage >= 0.50 else "Low coverage"
        reasons.insert(0, f"Score uses {len(components)} available component(s); weights were normalized to exclude unknown information.")

    if not opportunity.get("deadline"):
        reasons.append("Deadline not identified; confirm it manually.")
    if not opportunity.get("organization"):
        reasons.append("Organization not confidently extracted; confirm the publisher before applying.")

    return {
        "score": score,
        "confidence": confidence,
        "component_coverage": round(available_weight / sum(WEIGHTS.values()), 2) if available_weight else 0.0,
        "components": components,
        "reasons": reasons,
    }
