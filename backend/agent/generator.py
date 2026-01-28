from models.router import get_generator
import re

FORBIDDEN_ENDINGS = ["en", "que", "de", "à", "pour", "mais"]

def clean_line(line: str) -> str:
    line = re.sub(r"^(here are.*?:)", "", line.lower()).strip()
    line = re.sub(r"^[0-9]+\.", "", line).strip()
    return line

def is_complete_sentence(text: str) -> bool:
    words = text.split()
    if len(words) < 6:
        return False
    if words[-1] in FORBIDDEN_ENDINGS:
        return False
    return True

def apply_silence(text: str) -> str:
    # retire le point final ou un mot évident
    text = text.rstrip(".")
    words = text.split()
    if len(words) > 6:
        return " ".join(words[:-1])
    return text

def generate_variants(subject: str, modes: list[str], n: int = 5):
    model = get_generator()

    prompt = f"""
Sujet : {subject}

Écris 5 tweets directement postables sur X.

Contraintes :
- Une seule phrase
- Ton humain, observateur
- Pas d’explication
- Pas de morale
- Pas de hashtag
- Pas d’emoji
- Français naturel

Donne UNIQUEMENT les tweets, un par ligne.
"""

    text = model.generate(prompt)
    if not text:
        return []

    tweets = []
    for raw in text.split("\n"):
        clean = clean_line(raw)
        if not is_complete_sentence(clean):
            continue

        tweets.append(clean)
        tweets.append(apply_silence(clean))

    # déduplication
    final = []
    seen = set()
    for t in tweets:
        key = t.lower()
        if key not in seen and len(t.split()) >= 5:
            seen.add(key)
            final.append(t)

    return final[:5]
