import random

OPENERS = [
    "Personne n’en parle mais",
    "On ne le dit pas assez :",
    "Ce qui choque vraiment, c’est que",
    "Le vrai problème, c’est que",
]

ENDERS = [
    "",
    " Et tout le monde fait semblant de ne rien voir.",
    " Mais personne n’ose le dire.",
    " Et ça dérange.",
]

def remix(tweet: str) -> str:
    t = tweet.strip()

    if len(t.split()) < 6:
        return t

    opener = random.choice(OPENERS)
    ender = random.choice(ENDERS)

    return f"{opener} {t[0].lower() + t[1:]}{ender}"
