
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TINYFISH_API_KEY")

if not api_key:
    raise SystemExit("Missing TINYFISH_API_KEY in .env")

response = requests.post(
    "https://api.fetch.tinyfish.ai",
    headers={
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    },
    json={
        "urls": ["https://www.tinyfish.ai/"],
        "format": "markdown",
    },
    timeout=120,
)

print("HTTP status:", response.status_code)
response.raise_for_status()

data = response.json()

for result in data.get("results", []):
    print("\nTitle:", result.get("title", "Untitled"))
    print("URL:", result.get("url", "No URL"))
    print("Content preview:")
    print((result.get("text") or "")[:1500])

if data.get("errors"):
    print("\nFetch errors:", data["errors"])
