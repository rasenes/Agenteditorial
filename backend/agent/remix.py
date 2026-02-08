import random

PATTERNS = [
    "Personne ne parle de ça, mais {}",
    "On ne vous dira jamais que {}",
    "Tout le monde débat de {}, mais personne ne voit le vrai problème",
    "Ce n’est pas {}, c’est bien pire",
    "{}. Et ça dit beaucoup de notre époque."
]


def remix(text: str) -> str:
    pattern = random.choice(PATTERNS)
    core = text.strip().rstrip(".")
    return pattern.format(core)
