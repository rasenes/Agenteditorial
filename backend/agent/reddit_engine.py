import requests

HEADERS = {"User-Agent": "agent-editorial/1.0"}

SUBREDDITS = [
    "france",
    "unpopularopinion",
    "confession",
    "technology",
]

def fetch_reddit_ideas(limit=5):
    ideas = []

    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/top.json?t=day&limit={limit}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            continue

        data = r.json()
        for post in data.get("data", {}).get("children", []):
            title = post["data"].get("title")
            if title and len(title.split()) > 5:
                ideas.append(title)

    return ideas
