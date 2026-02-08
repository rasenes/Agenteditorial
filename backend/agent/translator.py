# backend/agent/translator.py
from typing import List
from providers.ollama import generate


def translate_to_fr(texts: List[str]) -> List[str]:
    """
    Traduit une liste de textes vers le français proprement
    (reste sur Ollama uniquement)
    """
    translated = []

    for text in texts:
        prompt = (
            "Traduis le texte suivant en français naturel, fluide et moderne. "
            "Ne rajoute rien.\n\n"
            f"TEXTE:\n{text}"
        )

        try:
            fr = generate(prompt)
            translated.append(fr.strip())
        except Exception:
            translated.append(text)  # fallback sécurisé

    return translated
