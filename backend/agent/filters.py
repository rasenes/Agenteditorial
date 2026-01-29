import re


def clean_line(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^[-•\d.]+", "", text)
    return text.strip(" \"'“”")


def is_complete_sentence(text: str) -> bool:
    return text.endswith((".", "!", "?"))


BLACKLIST = [
    "selon",
    "a déclaré",
    "communiqué",
    "rapport",
    "conférence",
    "porte-parole",
    "déclaration",
]


def filter_variants(tweets: list[str]) -> list[str]:
    final = []
    seen = set()

    for t in tweets:
        low = t.lower()

        if any(b in low for b in BLACKLIST):
            continue

        key = " ".join(low.split()[:6])
        if key in seen:
            continue

        seen.add(key)
        final.append(t)

    return final

def score_tweet(tweet: str) -> int:
    score = 0
    length = len(tweet.split())

    # longueur idéale Twitter
    if 8 <= length <= 20:
        score += 3
    elif length < 6:
        score -= 2

    # ponctuation qui crée une tension
    if "?" in tweet:
        score += 2
    if "…" in tweet or "..." in tweet:
        score += 1

    # mots faibles (langue molle)
    weak_words = ["devrait", "semble", "pourrait", "souhaite"]
    if any(w in tweet.lower() for w in weak_words):
        score -= 3

    # fin forte
    if tweet.strip().endswith(("?", "!", ".")):
        score += 1

    return score
