
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TINYFISH_API_KEY")

if not api_key:
    raise SystemExit(
        "Missing TINYFISH_API_KEY. Check your .env file."
    )

response = requests.get(
    "https://api.search.tinyfish.ai",
    headers={"X-API-Key": api_key},
    params={
        "query": (
            "official university scholarships "
            "2026 application deadline"
        )
    },
    timeout=30,
)

print("HTTP status:", response.status_code)
response.raise_for_status()

data = response.json()

print("\nSearch results:")
for result in data.get("results", [])[:5]:
    print("\nTitle:", result.get("title", "Untitled"))
    print("URL:", result.get("url", "No URL"))
    print("Snippet:", result.get("snippet", "No snippet"))
