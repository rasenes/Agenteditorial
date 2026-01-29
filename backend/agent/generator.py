from providers.ollama import generate
from agent.filters import clean_line, is_complete_sentence

PROMPT_TEMPLATE = """
Tu écris comme une vraie personne sur Twitter/X.

Sujet :
"{subject}"

Angle :
{mode}

Règles absolues :
- Une seule phrase
- Ton naturel, jamais scolaire
- Pas de morale
- Pas d'introduction
- Pas de conclusion
- Pas d'emojis
- Pas de hashtags
- Français courant

Style selon l'angle :
- journalisme : précis, factuel, sans émotion inutile
- miroir : question qui met mal à l'aise
- meta_systeme : regard froid sur le système
- confession : intime, humain, presque vulnérable
- humour_noir : ironique, sec, un peu cruel
- minimal : très court, brut
- business_froid : pragmatique, presque cynique

Donne UNIQUEMENT des tweets, un par ligne.
"""

def generate_variants(subject: str, modes: list[str], n: int = 5) -> list[str]:
    tweets = []

    for mode in modes:
        prompt = PROMPT_TEMPLATE.format(subject=subject, mode=mode)
        text = generate(prompt)

        if not text:
            continue

        for raw in text.split("\n"):
            clean = clean_line(raw)
            if not is_complete_sentence(clean):
                continue
            tweets.append(clean)

    # Déduplication
    final = []
    seen = set()
    for t in tweets:
        key = t.lower()
        if key not in seen and len(t.split()) >= 5:
            seen.add(key)
            final.append(t)

    return final[:n]
