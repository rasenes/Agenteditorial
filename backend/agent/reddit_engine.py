import requests

HEADERS = {"User-Agent": "agent-editorial/1.0"}

def fetch_reddit(subreddit: str, limit: int = 5) -> list[str]:
    url = f"https://www.reddit.com/r/{subreddit}/top.json?limit={limit}&t=day"
    r = requests.get(url, headers=HEADERS)
    data = r.json()

    ideas = []
    for post in data.get("data", {}).get("children", []):
        title = post["data"].get("title")
        if title:
            ideas.append(title)

    return ideas
