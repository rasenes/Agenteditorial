import re

POWER_WORDS = [
    "personne", "tout le monde", "jamais", "toujours",
    "réalité", "vérité", "problème", "absurde", "grave"
]

def score_tweet(tweet: str) -> int:
    score = 0
    t = tweet.lower()

    # Longueur idéale Twitter
    if 70 <= len(tweet) <= 200:
        score += 2

    # Question = engagement
    if "?" in tweet:
        score += 2

    # Mots puissants
    for w in POWER_WORDS:
        if w in t:
            score += 1

    # Trop journalistique = malus
    if re.search(r"\b(selon|a déclaré|communiqué|officiel)\b", t):
        score -= 2

    # Trop neutre
    if tweet.endswith("."):
        score -= 1

    return score


def rank_tweets(tweets: list[str], top_k=5) -> list[str]:
    ranked = sorted(tweets, key=score_tweet, reverse=True)
    return ranked[:top_k]
