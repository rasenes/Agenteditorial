import re

POWER_WORDS = [
    "liberté", "argent", "peur", "vérité", "silence",
    "interdit", "pouvoir", "contrôle", "hypocrisie"
]

def score_tweet(tweet: str) -> int:
    score = 0
    t = tweet.lower()

    # longueur idéale
    if 8 <= len(tweet.split()) <= 22:
        score += 2

    # ponctuation engageante
    if "?" in tweet:
        score += 1
    if "!" in tweet:
        score += 1

    # mots puissants
    for w in POWER_WORDS:
        if w in t:
            score += 1

    # pas trop journalistique
    if re.search(r"\b(selon|a annoncé|a déclaré)\b", t):
        score -= 2

    return score


def rank_tweets(tweets: list[str], top_k: int = 5) -> list[str]:
    scored = [(score_tweet(t), t) for t in tweets]
    scored.sort(reverse=True)
    return [t for _, t in scored[:top_k]]

ANGLE_BONUS = {
    "confession": 2,
    "opinion_impopulaire": 2,
    "observation_froide": 1,
    "meta_systeme": 1,
    "journalisme": -1,
}

def score_with_angle(tweet: str, angle: str) -> int:
    base = score_tweet(tweet)
    bonus = ANGLE_BONUS.get(angle, 0)
    return base + bonus

