# backend/agent/filters.py

import re


def filter_variants(drafts: list[str]) -> list[str]:
    clean = []

    for t in drafts:
        if not isinstance(t, str):
            continue

        t = t.strip()

        # Trop court
        if len(t.split()) < 6:
            continue

        # Phrase coupée
        if t.endswith(("mais", "et", "ou", "de", "que", "pour")):
            continue

        # Trop journalistique sec
        t = soften_journalism(t)

        # Trop générique
        blacklist = [
            "tout est une question",
            "le jeu est éternel",
            "en fin de compte",
            "au final",
        ]
        if any(b in t.lower() for b in blacklist):
            continue

        clean.append(t)

    return deduplicate(clean)


def soften_journalism(tweet: str) -> str:
    replacements = {
        "a décidé de": "vient de",
        "a rejeté": "a fermé la porte à",
        "a annoncé": "laisse entendre",
        "selon les autorités": "d'après ce qu'on sait",
        "le débat est renvoyé": "le débat continue",
    }

    for k, v in replacements.items():
        tweet = tweet.replace(k, v)

    return tweet


def deduplicate(tweets: list[str]) -> list[str]:
    seen = set()
    unique = []

    for t in tweets:
        key = " ".join(t.lower().split()[:5])
        if key in seen:
            continue
        seen.add(key)
        unique.append(t)

    return unique
