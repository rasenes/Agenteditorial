def detect_language(text: str) -> str:
    t = text.lower()

    if any(w in t for w in [" the ", " and ", " is ", " are "]):
        return "en"
    if any(w in t for w in [" el ", " la ", " que ", " por "]):
        return "es"
    if any(w in t for w in [" der ", " die ", " und "]):
        return "de"
    if any(w in t for w in [" che ", " non ", " per "]):
        return "it"

    return "fr"
