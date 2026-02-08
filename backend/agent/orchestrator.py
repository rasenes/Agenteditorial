# backend/agent/orchestrator.py
from typing import Dict

from agent.sources_registry import fetch_all_sources
from agent.generator import generate_variants
from agent.translator import translate_to_fr
from agent.scoring import rank_tweets


def run_agent(subject: str) -> Dict:
    # 1️⃣ Récupération des sources (RSS etc.)
    sources = fetch_all_sources()

    raw_ideas = [
        s.get("title") or s.get("summary", "")
        for s in sources
        if s.get("title") or s.get("summary")
    ]

    # 2️⃣ Génération de tweets
    tweets = generate_variants(
        subject=subject,
        modes=["observation", "ironie", "minimal"],
        n=10
    )

    # 3️⃣ Traduction finale en français
    tweets_fr = translate_to_fr(tweets)

    # 4️⃣ Scoring
    top = rank_tweets(tweets_fr, top_k=5)

    return {
        "analysis": "Observation générale",
        "tweets": tweets_fr,
        "top_tweets": top,
    }
