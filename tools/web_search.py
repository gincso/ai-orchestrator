import httpx
from tools.registry import register_tool


def web_search(query: str, num_results: int = 5) -> str:
    try:
        resp = httpx.get(
            "https://api.duckduckgo.com",
            params={"q": query, "format": "json", "no_html": 1},
            timeout=10,
        )
        data = resp.json()
        results = []
        for topic in data.get("RelatedTopics", [])[:num_results]:
            if "Text" in topic and "FirstURL" in topic:
                results.append(f"- {topic['Text']} ({topic['FirstURL']})")
        return "\n".join(results) if results else f"No results for '{query}'."
    except Exception as e:
        return f"Search error: {e}"


def fetch_url(url: str) -> str:
    try:
        resp = httpx.get(url, timeout=15, follow_redirects=True)
        text = resp.text[:5000]
        return text
    except Exception as e:
        return f"Fetch error: {e}"


register_tool(
    name="web_search",
    description="Search the web for information on a topic",
    fn=web_search,
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "num_results": {"type": "integer", "description": "Number of results"},
        },
        "required": ["query"],
    },
)

register_tool(
    name="fetch_url",
    description="Fetch and return the content of a URL",
    fn=fetch_url,
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL to fetch"},
        },
        "required": ["url"],
    },
)
