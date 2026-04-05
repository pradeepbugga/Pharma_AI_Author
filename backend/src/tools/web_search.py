
import requests
import os
import time

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# we use Tavily API to do web search with our LLM as fallback

def lookup_web_search(entity: str, session=None) -> dict:
   
    if session is None:
        session = requests.Session()

    url = "https://api.tavily.com/search"

    # Focused queries for drug/intervention detection -> note: this can be modified for the scientific area
    queries = [
        f"{entity} inhibitor drug",
        f"{entity} compound study cancer",
        f"{entity} mechanism of action"
    ]

    results = []

    for attempt in range(3):

        try:
            for q in queries:
                payload = {
                    "api_key": TAVILY_API_KEY,
                    "query": q,
                    "search_depth": "basic",
                    "max_results": 2  # this can be adjusted based on how much info we want to feed into the LLM, keeping it small for now
                }

                res = session.post(url, json=payload, timeout=10)
                res.raise_for_status()
                data = res.json()

                for r in data.get("results", []):
                    results.append({
                        "title": r.get("title"),
                        "snippet": r.get("content"),
                        "url": r.get("url")
                    })

            # Deduplicate by URL since sometimes different queries can return the same result
            seen = set()
            deduped = []
            for r in results:
                if r["url"] not in seen:
                    seen.add(r["url"])
                    deduped.append(r)

            return {
                "found": len(deduped) > 0,
                "results": deduped[:5],  # keep small for LLM input, can be adjusted
                "source": "web"
            }

        except Exception as e:
            if attempt == 2:
                return {
                    "found": False,
                    "error": str(e)
                }
            time.sleep(2 ** attempt)  # exponential backoff