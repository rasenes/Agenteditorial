import feedparser

def fetch_rss(url: str, limit: int = 5) -> list[str]:
    feed = feedparser.parse(url)
    ideas = []

    for entry in feed.entries[:limit]:
        title = entry.get("title", "")
        if title:
            ideas.append(title)

    return ideas
