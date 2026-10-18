import re
from urllib.parse import urlparse

URL_RE = re.compile(r"https?://[^\s<>\]\)\"']+", re.IGNORECASE)
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,})", re.IGNORECASE)
DATE_PATTERNS = [
    r"(?:closes?|closing|deadline is|apply)\s+(today|tomorrow)[.!]?",
    r"(?:deadline|apply by|applications close|last date|due date)\s*[:\-]?\s*([^\n.;]{3,60})",
    r"(?:by|before)\s+((?:\d{1,2}[ /-])?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(?:\s+\d{1,2})?(?:,?\s+\d{4})?)",
    r"(?:deadline|due)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
]

def extract_opportunity(text: str) -> dict:
    """Conservative, dependency-light extraction baseline. LLM extraction can replace this later."""
    urls = URL_RE.findall(text)
    domains = []
    for match in EMAIL_RE.findall(text):
        if match.lower() not in domains:
            domains.append(match.lower())
    for url in urls:
        host = urlparse(url).netloc.lower().removeprefix("www.")
        if host and host not in domains:
            domains.append(host)
    deadline = None
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            deadline = match.group(1).strip()
            break
    lines = [re.sub(r"\s+", " ", line).strip(" -*\t") for line in text.splitlines() if line.strip()]
    title = None
    for line in lines[:12]:
        if len(line) < 120 and re.search(r"\b(intern|internship|scholarship|fellowship|research|hackathon|grant|engineer|analyst|program|opportunity|job|role|carnival)\b", line, re.I):
            candidate = line
            # Remove common email prose so the title is closer to the named opportunity.
            candidate = re.sub(r"^(?:hi[,!]?\s+)?(?:the\s+)?(?:application window for|applications for|apply for|introducing|announcing)\s+(?:the\s+)?", "", candidate, flags=re.I)
            candidate = re.sub(r"\s+(?:closes?|closing|ends?|is closing)\s+(?:today|tomorrow|soon|on\b.*)[.!?]?$", "", candidate, flags=re.I)
            candidate = re.sub(r"\s+(?:is now open|now open|applications? open).*$", "", candidate, flags=re.I)
            candidate = candidate.strip(" .:—–-")
            title = candidate or line
            break
    organization = None
    org_match = re.search(r"(?:from|at|organization|company|host)\s*[:\-]?\s*([A-Z][A-Za-z0-9&.,' -]{2,60})", text)
    if org_match:
        organization = org_match.group(1).strip().split("\n")[0][:80]
    low = text.lower()
    types = [("Internship", "intern"), ("Scholarship", "scholarship"), ("Research", "research"), ("Fellowship", "fellowship"), ("Hackathon", "hackathon"), ("Grant", "grant"), ("Job", "job")]
    opp_type = next((label for label, needle in types if needle in low), None)
    return {
        "title": title,
        "organization": organization,
        "type": opp_type,
        "deadline": deadline,
        "application_url": urls[0] if urls else None,
        "urls": urls,
        "domains": domains,
        "raw_text": text,
    }
