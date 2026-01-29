import feedparser

DEFAULT_RSS = [
    "https://www.lemonde.fr/rss/une.xml",
    "https://www.francetvinfo.fr/titres.rss",
    "https://hnrss.org/frontpage",
]

def fetch_rss_ideas(limit_per_feed=3):
    ideas = []

    for url in DEFAULT_RSS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:limit_per_feed]:
            title = entry.get("title")
            if title and len(title.split()) > 4:
                ideas.append(title)

    return ideas
