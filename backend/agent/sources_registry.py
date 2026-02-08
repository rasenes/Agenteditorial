# backend/agent/sources_registry.py
from typing import List, Dict

from agent.rss_engine import fetch_rss
# plus tard :
# from agent.reddit_engine import fetch_reddit
# from agent.newsapi_engine import fetch_newsapi


def fetch_all_sources() -> List[Dict]:
    """
    Centralise toutes les sources d'idées
    """
    ideas: List[Dict] = []

    try:
        ideas.extend(fetch_rss())
    except Exception as e:
        print(f"[RSS ERROR] {e}")

    # futures sources ici
    # ideas.extend(fetch_reddit())
    # ideas.extend(fetch_newsapi())

    return ideas
