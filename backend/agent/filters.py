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
