import re
from typing import List


# =========================
# Nettoyage de base
# =========================

def clean_line(text: str) -> str:
    if not text:
        return ""

    t = text.strip()

    # Supprimer guillemets et listes
    t = re.sub(r'^[-•"\']+', '', t)
    t = re.sub(r'["\']+$', '', t)

    # Espaces multiples
    t = re.sub(r"\s+", " ", t)

    # Journalisme léger → langage humain
    t = soften_journalism(t)

    return t.strip()


def is_complete_sentence(text: str) -> bool:
    if len(text.split()) < 6:
        return False

    if text.endswith(","):
        return False

    return True


# =========================
# Anti-journalisme
# =========================

def soften_journalism(tweet: str) -> str:
    replacements = {
        "selon": "",
        "aurait": "",
        "il est important de": "",
        "il convient de": "",
        "on peut se demander": "",
        "cela pose la question": "",
        "le débat est ouvert": "",
        "en fin de compte": "",
        "au final": "",
    }

    lower = tweet.lower()
    for k, v in replacements.items():
        if k in lower:
            tweet = re.sub(k, v, tweet, flags=re.IGNORECASE)

    return tweet.strip()


# =========================
# Scoring Twitter (🔥)
# =========================

STRONG_VERBS = [
    "détruit", "explose", "révèle", "impose", "trahit",
    "prouve", "montre", "enterre", "confirme"
]

SOFT_PATTERNS = [
    "il faut",
    "il serait",
    "il est important",
    "on devrait",
    "cela montre que",
    "il s'agit de",
]


def punch_score(tweet: str) -> int:
    score = 0
    lower = tweet.lower()

    # Verbes forts
    if any(v in lower for v in STRONG_VERBS):
        score += 2

    # Ponctuation Twitter
    if "?" in tweet or "!" in tweet:
        score += 1

    # Longueur idéale Twitter
    if 8 <= len(tweet.split()) <= 22:
        score += 1

    # Phrases molles → pénalité
    if any(p in lower for p in SOFT_PATTERNS):
        score -= 2

    return score


# =========================
# Filtrage final
# =========================

def filter_tweets(tweets: List[str], min_score: int = 1) -> List[str]:
    cleaned = []

    for t in tweets:
        if not t:
            continue

        score = punch_score(t)

        if score < min_score:
            continue

        cleaned.append(t)

    return deduplicate(cleaned)


def deduplicate(tweets: List[str]) -> List[str]:
    seen = set()
    unique = []

    for t in tweets:
        key = " ".join(t.lower().split()[:5])
        if key in seen:
            continue
        seen.add(key)
        unique.append(t)

    return unique
