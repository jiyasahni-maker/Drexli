"""Evidence-oriented opportunity review using TinyFish Search and Fetch.

This module deliberately avoids treating the presence of search results or a trusted-looking
TLD as proof. It scores source relevance and reports individual claims separately.
"""
from datetime import datetime, timezone
from urllib.parse import urlparse
import re

STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "at", "by",
    "is", "are", "was", "be", "with", "your", "apply", "application", "applications",
    "window", "closes", "close", "deadline", "official", "website", "today", "tomorrow",
    "opportunity", "program", "programme", "position", "open", "now", "this", "that",
}


def _norm(text):
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _tokens(text):
    return {token for token in re.findall(r"[a-z0-9]+", _norm(text)) if len(token) > 2 and token not in STOPWORDS}


def _host(url):
    return urlparse(url or "").netloc.lower().removeprefix("www.")


def _source_relevance(opportunity, source):
    """Return a conservative relevance score and explanation, not a trust score."""
    title = _norm(opportunity.get("title"))
    org = _norm(opportunity.get("organization"))
    source_text = _norm(" ".join([
        source.get("title", ""), source.get("snippet", ""), source.get("text", "")[:5000]
    ]))
    title_tokens = _tokens(title)
    org_tokens = _tokens(org)
    source_tokens = _tokens(source_text)
    title_overlap = len(title_tokens & source_tokens) / len(title_tokens) if title_tokens else 0.0
    org_exact = bool(org and len(org) >= 4 and org in source_text)
    org_overlap = len(org_tokens & source_tokens) / len(org_tokens) if org_tokens else 0.0

    score = 0.0
    reasons = []
    if org_exact:
        score += 0.65
        reasons.append("organization name appears in source")
    elif org_tokens and org_overlap >= 0.75:
        score += 0.35
        reasons.append("most organization-name terms appear in source")
    if title_overlap >= 0.67:
        score += 0.45
        reasons.append("most distinctive title terms appear in source")
    elif title_overlap >= 0.34:
        score += 0.20
        reasons.append("some title terms appear in source")

    # Avoid classifying a generic source as relevant based on only one common word.
    min_title_matches = 1 if len(title_tokens) <= 2 else 2
    title_matches = len(title_tokens & source_tokens)
    relevant = org_exact or (title_matches >= min_title_matches and title_overlap >= 0.34)
    if not title_tokens and not org_tokens:
        relevant = False
    return min(score, 1.0), relevant, "; ".join(reasons) if reasons else "no distinctive listing details matched"


def verify_opportunity(client, opportunity, raw_text):
    title = (opportunity.get("title") or "").strip()
    org = (opportunity.get("organization") or "").strip()
    opp_type = (opportunity.get("type") or "").strip()
    supplied_url = (opportunity.get("application_url") or "").strip()

    query_terms = [f'"{title}"' if title else ""]
    if org:
        query_terms.append(f'"{org}"')
    if opp_type:
        query_terms.append(opp_type.lower())
    query_terms.append("official application deadline")
    query = " ".join(term for term in query_terms if term)

    search_results = client.search(query, limit=6)
    candidate_urls = []
    if supplied_url:
        candidate_urls.append(supplied_url)
    candidate_urls.extend(result.get("url", "") for result in search_results[:5])
    candidate_urls = list(dict.fromkeys(url for url in candidate_urls if url))[:6]
    fetched = client.fetch(candidate_urls)

    # Index fetched pages by requested and final URL to handle redirects.
    fetched_by_url = {}
    for page in fetched:
        for key in (page.get("url"), page.get("final_url")):
            if key:
                fetched_by_url[key] = page

    combined_sources = []
    seen_urls = set()
    for result in search_results:
        url = result.get("url", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        page = fetched_by_url.get(url, {})
        combined_sources.append({
            "title": page.get("title") or result.get("title", ""),
            "url": page.get("final_url") or page.get("url") or url,
            "snippet": (page.get("text") or result.get("snippet") or "Search result; page content unavailable")[:700],
            "text": page.get("text", ""),
            "source_type": "Search result + fetched page" if page else "Search result (page not fetched)",
        })
    for page in fetched:
        url = page.get("final_url") or page.get("url", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        combined_sources.append({
            "title": page.get("title", ""), "url": url,
            "snippet": (page.get("text") or "Fetched page")[:700],
            "text": page.get("text", ""), "source_type": "Fetched page",
        })

    assessed_sources = []
    for source in combined_sources:
        score, relevant, reason = _source_relevance(opportunity, source)
        assessed_sources.append({
            "title": source["title"] or source["url"],
            "url": source["url"],
            "snippet": source["snippet"],
            "source_type": source["source_type"],
            "relevance_score": round(score, 2),
            "relevant": relevant,
            "relevance_reason": reason,
            "source_text": source.get("text", "")[:15000],
        })

    relevant_sources = [source for source in assessed_sources if source["relevant"]]
    relevant_text = "\n".join(
        _norm(source.get("title", "") + " " + source.get("snippet", "") + " " + source.get("source_text", ""))
        for source in relevant_sources
    )

    # Conservative claim checks. These are signals, not proof of authenticity.
    claim_checks = []
    if org:
        org_supported = _norm(org) in relevant_text
        claim_checks.append({"claim": f"Organization: {org}", "status": "Corroborated" if org_supported else "Unverified",
                             "explanation": "Organization name appears in relevant source text." if org_supported else "No relevant source clearly names this organization."})
    else:
        claim_checks.append({"claim": "Organization identity", "status": "Missing information",
                             "explanation": "The listing parser did not identify an organization."})

    deadline = (opportunity.get("deadline") or "").strip()
    if deadline:
        deadline_supported = _norm(deadline) in relevant_text
        claim_checks.append({"claim": f"Deadline: {deadline}", "status": "Corroborated" if deadline_supported else "Unverified",
                             "explanation": "Deadline text appears in relevant source content." if deadline_supported else "No relevant source explicitly confirmed this deadline text."})
    else:
        claim_checks.append({"claim": "Application deadline", "status": "Missing information",
                             "explanation": "No deadline was confidently extracted from the listing."})

    if supplied_url:
        supplied_host = _host(supplied_url)
        independently_found = any(_host(source["url"]) == supplied_host and source["relevant"] for source in assessed_sources)
        url_supported = independently_found
        claim_checks.append({"claim": f"Application URL: {supplied_url}", "status": "Corroborated" if url_supported else "Unverified",
                             "explanation": "The supplied domain was fetched or appeared in relevant evidence." if url_supported else "The supplied application domain was not independently corroborated by relevant evidence."})
    else:
        claim_checks.append({"claim": "Application URL", "status": "Missing information",
                             "explanation": "No application URL was confidently extracted from the listing."})

    corroborated_count = sum(1 for claim in claim_checks if claim["status"] == "Corroborated")
    if relevant_sources and corroborated_count:
        status = "Relevant evidence found — review claims"
        summary = ("Drexli found sources that appear relevant and some listing details with supporting text. This is not a guarantee of legitimacy; "
                   "inspect each source and confirm it is controlled by the claimed organization.")
    elif relevant_sources:
        status = "Relevant sources found — claims unconfirmed"
        summary = ("Some sources appear relevant to this opportunity, but the checked claims were not explicitly corroborated. "
                   "Verify details on the organization's official website before sharing sensitive information or paying fees.")
    elif search_results or fetched:
        status = "Unverified — no relevant evidence found"
        summary = ("Drexli retrieved webpages, but could not establish that they support this listing. Unrelated search results are not corroboration. "
                   "This does not, by itself, mean the opportunity is fraudulent.")
    else:
        status = "Unable to verify — no evidence retrieved"
        summary = "Drexli could not retrieve evidence to assess this listing. This does not, by itself, mean the opportunity is fraudulent."

    signals = []
    if relevant_sources:
        signals.append(f"Found {len(relevant_sources)} source(s) with matching listing details.")
    else:
        signals.append("No retrieved source matched enough distinctive details to be treated as relevant evidence.")
    if not org:
        signals.append("Organization identity was not extracted; confirm the publisher manually.")
    if not deadline:
        signals.append("Deadline was not extracted; confirm it manually.")
    if not supplied_url:
        signals.append("Application URL was not extracted; locate it through the organization's official website.")
    signals.append("A relevant source is not automatically an authentic source; inspect publisher identity and the application domain.")

    # Keep full fetched text out of the object persisted by the tracker/UI.
    for source in assessed_sources:
        source.pop("source_text", None)

    return {
        "status": status,
        "summary": summary,
        "signals": signals,
        "sources": assessed_sources,
        "claim_checks": claim_checks,
        "relevant_source_count": len(relevant_sources),
        "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "search_results": search_results,
        "query": query,
    }
