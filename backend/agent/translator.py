from providers.ollama import generate

TRANSLATE_PROMPT = """
Traduis le texte suivant en français.
Garde un ton naturel, courant, Twitter.
Pas de commentaire, pas d'explication.

Texte :
{text}
"""

def translate_to_french(text: str, lang: str) -> str:
    if lang == "fr":
        return text

    prompt = TRANSLATE_PROMPT.format(text=text)
    translated = generate(prompt)

    return translated.strip() if translated else text
