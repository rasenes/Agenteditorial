import re

STRONG_WORDS = [
    "personne n'en parle",
    "le vrai problème",
    "ce qui dérange",
    "on fait semblant",
    "c'est fou",
    "absurde",
    "hypocrite",
]

WEAK_STARTS = [
    "selon",
    "il est important",
    "il faut rappeler",
    "rappelons que",
]

QUESTION_BONUS = 0.15
STRONG_WORD_BONUS = 0.1
WEAK_START_PENALTY = 0.3


def score_tweet(tweet: str) -> float:
    score = 1.0

    t = tweet.lower()

    if "?" in tweet:
        score += QUESTION_BONUS

    for w in STRONG_WORDS:
        if w in t:
            score += STRONG_WORD_BONUS

    for w in WEAK_STARTS:
        if t.startswith(w):
            score -= WEAK_START_PENALTY

    score += min(len(tweet) / 280, 1) * 0.2

    return round(score, 2)


def rank_tweets(tweets: list[str], top_k: int = 5) -> list[str]:
    ranked = sorted(tweets, key=score_tweet, reverse=True)
    return ranked[:top_k]
