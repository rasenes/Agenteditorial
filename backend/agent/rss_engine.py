# backend/agent/rss_engine.py
import feedparser
from typing import List, Dict


def fetch_rss() -> List[Dict]:
    """
    Récupère des articles RSS et retourne une liste d'idées brutes
    """
    feeds = [
        "https://www.lemonde.fr/rss/une.xml",
        "https://www.francetvinfo.fr/titres.rss",
        "https://feeds.bbci.co.uk/news/rss.xml",
    ]

    results = []

    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            results.append({
                "source": "rss",
                "title": entry.get("title", ""),
                "summary": entry.get("summary", "")
            })

    return results
