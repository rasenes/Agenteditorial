import os
import requests

NEWS_API_KEY = os.getenv("NEWSAPI_KEY")

def fetch_newsapi():
    if not NEWS_API_KEY:
        return []

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "language": "en",
        "pageSize": 10,
        "apiKey": NEWS_API_KEY
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    return [
        {
            "source": "newsapi",
            "lang": "en",
            "text": a["title"]
        }
        for a in data.get("articles", [])
        if a.get("title")
    ]
