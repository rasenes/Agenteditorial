from agent.rss_trends import fetch_rss_trends


def get_trends(source: str = "rss") -> list[str]:
    if source == "rss":
        return fetch_rss_trends()

    return []
