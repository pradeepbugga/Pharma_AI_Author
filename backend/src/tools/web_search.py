
import requests
import os

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def lookup_web_search(entity: str, session=None) -> dict:
    """
    Retrieve lightweight biomedical evidence about an entity.
    Used ONLY when other tools (PubChem/UniProt) are insufficient.
    """

    if session is None:
        session = requests.Session()

    url = "https://api.tavily.com/search"

    # Focused queries for drug/intervention detection
    queries = [
        f"{entity} inhibitor drug",
        f"{entity} compound study cancer",
        f"{entity} mechanism of action"
    ]

    results = []

    try:
        for q in queries:
            payload = {
                "api_key": TAVILY_API_KEY,
                "query": q,
                "search_depth": "basic",
                "max_results": 2
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

        # Deduplicate by URL
        seen = set()
        deduped = []
        for r in results:
            if r["url"] not in seen:
                seen.add(r["url"])
                deduped.append(r)

        return {
            "found": len(deduped) > 0,
            "results": deduped[:5],  # keep small for LLM
            "source": "web"
        }

    except Exception as e:
        return {
            "found": False,
            "error": str(e)
        }