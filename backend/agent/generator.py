from typing import List

from providers.ollama import generate
from agent.filters import clean_line, is_complete_sentence, filter_tweets


PROMPT_TEMPLATE = """
Tu es un excellent utilisateur de Twitter/X.

Sujet :
{subject}

Angle :
{mode}

Contraintes :
- Pas journalistique
- Pas neutre
- Pas d'introduction
- Pas de conclusion
- Une seule phrase
- Ton humain
- Français naturel
- Pas de hashtags
- Pas d'emojis

Donne UNIQUEMENT les tweets, un par ligne.
"""


def generate_variants(
    subject: str,
    modes: List[str],
    n: int = 5
) -> List[str]:

    tweets = []

    for mode in modes:
        prompt = PROMPT_TEMPLATE.format(
            subject=subject,
            mode=mode
        )

        text = generate(prompt)
        if not text:
            continue

        for raw in text.split("\n"):
            clean = clean_line(raw)
            if not is_complete_sentence(clean):
                continue
            tweets.append(clean)

    # 🔥 Filtrage Twitter PRO
    tweets = filter_tweets(tweets, min_score=1)

    return tweets[:n]
