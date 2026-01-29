REMIX_PATTERNS = [
    "On a normalisé le fait que {idea}.",
    "Personne ne veut l'admettre mais {idea}.",
    "Le problème n'est pas {fake}, c'est {idea}.",
    "{idea}. Mais on préfère regarder ailleurs.",
]


def remix_idea(idea: str) -> list[str]:
    return [p.format(idea=idea, fake="le détail") for p in REMIX_PATTERNS]
