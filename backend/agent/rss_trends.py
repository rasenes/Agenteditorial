import feedparser

RSS_FEEDS = {
    "news": "https://news.google.com/rss?hl=fr&gl=FR&ceid=FR:fr",
    "tech": "https://news.google.com/rss/search?q=technologie&hl=fr&gl=FR&ceid=FR:fr",
    "business": "https://news.google.com/rss/search?q=business&hl=fr&gl=FR&ceid=FR:fr",
}


def fetch_rss_trends(limit: int = 5) -> list[str]:
    headlines = []

    for url in RSS_FEEDS.values():
        feed = feedparser.parse(url)
        for entry in feed.entries[:limit]:
            title = entry.get("title")
            if title:
                headlines.append(title)

    return headlines