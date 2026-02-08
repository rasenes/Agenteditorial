import re
from agent.memory_engine import load_memory


def _length_score(text: str) -> float:
    l = len(text)
    if 80 <= l <= 220:
        return 1.0
    if 60 <= l < 80 or 220 < l <= 260:
        return 0.7
    return 0.3


def _emotion_score(text: str) -> float:
    triggers = [
        "?", "!", "jamais", "toujours", "incroyable",
        "absurde", "folie", "vérité", "personne",
        "tout le monde", "ils", "on"
    ]
    return sum(1 for t in triggers if t in text.lower()) * 0.15


def _structure_score(text: str) -> float:
    if text.count("?") >= 1:
        return 0.5
    if ":" in text:
        return 0.4
    if text.startswith(("Pourquoi", "Personne", "On nous", "Tout le monde")):
        return 0.6
    return 0.2


def _memory_bonus(text: str) -> float:
    memory = load_memory()
    history = memory.get("history", [])

    for item in history[-50:]:
        if item["tweet"][:40].lower() in text.lower():
            return -0.5  # pénalité répétition

    return 0.3


def score_tweet(text: str) -> float:
    score = 0.0
    score += _length_score(text)
    score += _emotion_score(text)
    score += _structure_score(text)
    score += _memory_bonus(text)
    return score


def rank_tweets(tweets: list[str], top_k: int = 5) -> list[str]:
    scored = [(t, score_tweet(t)) for t in tweets]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [t for t, _ in scored[:top_k]]
