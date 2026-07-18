from tavily import TavilyClient

from app.config import get_settings


def search_market(idea: str, max_results: int = 5) -> list[dict]:
    settings = get_settings()
    if not settings.tavily_api_key:
        return [
            {
                "title": "Sample market note (Tavily key missing)",
                "url": "",
                "content": (
                    f"No live search ran. Treat this as a placeholder for: {idea}. "
                    "Set TAVILY_API_KEY for real competitor and market research."
                ),
            }
        ]

    client = TavilyClient(api_key=settings.tavily_api_key)
    queries = [
        f"{idea} market competitors startup",
        f"{idea} industry trends challenges",
    ]
    results: list[dict] = []
    seen: set[str] = set()
    for q in queries:
        try:
            resp = client.search(q, max_results=max_results, search_depth="basic")
        except Exception as exc:  # noqa: BLE001
            results.append({"title": "Search error", "url": "", "content": str(exc)})
            continue
        for item in resp.get("results", []):
            url = item.get("url") or ""
            if url in seen:
                continue
            seen.add(url)
            results.append(
                {
                    "title": item.get("title") or "",
                    "url": url,
                    "content": item.get("content") or "",
                }
            )
    return results[:12]
