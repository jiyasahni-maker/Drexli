import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TinyFishError(RuntimeError):
    pass

class TinyFishClient:
    SEARCH_URL = "https://api.search.tinyfish.ai"
    FETCH_URL = "https://api.fetch.tinyfish.ai"

    def __init__(self, api_key=None, timeout=35):
        self.api_key = api_key or os.getenv("TINYFISH_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise TinyFishError("TINYFISH_API_KEY is missing. Add it to your local .env file.")

    @property
    def headers(self):
        return {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    def search(self, query, limit=5):
        try:
            response = requests.get(self.SEARCH_URL, params={"query": query}, headers={"X-API-Key": self.api_key}, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise TinyFishError(f"TinyFish Search request failed: {exc}") from exc
        except ValueError as exc:
            raise TinyFishError("TinyFish Search returned invalid JSON.") from exc
        results = payload.get("results", [])
        return [{"title": x.get("title", ""), "url": x.get("url", ""), "snippet": x.get("snippet", ""), "site_name": x.get("site_name", "")} for x in results[:limit] if x.get("url")]

    def fetch(self, urls):
        urls = list(dict.fromkeys(url for url in urls if url))[:10]
        if not urls:
            return []
        try:
            response = requests.post(self.FETCH_URL, headers=self.headers, json={"urls": urls, "format": "markdown"}, timeout=max(self.timeout, 60))
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise TinyFishError(f"TinyFish Fetch request failed: {exc}") from exc
        except ValueError as exc:
            raise TinyFishError("TinyFish Fetch returned invalid JSON.") from exc
        return [{"url": x.get("url", ""), "final_url": x.get("final_url", ""), "title": x.get("title", ""), "text": x.get("text", ""), "format": x.get("format", "markdown")} for x in payload.get("results", [])]
