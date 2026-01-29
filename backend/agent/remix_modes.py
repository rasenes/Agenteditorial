def remix_silence(tweet: str) -> str:
    return tweet.replace(".", "").strip()

def remix_contraste(tweet: str) -> str:
    return f"Tout le monde parle de progrès.\n{tweet}"

def remix_question(tweet: str) -> str:
    if "?" in tweet:
        return tweet
    return f"{tweet} Vraiment ?"

REMIXERS = [
    remix_silence,
    remix_contraste,
    remix_question,
]

def remix_all(tweet: str) -> list[str]:
    results = []
    for fn in REMIXERS:
        try:
            t = fn(tweet)
            if t and t != tweet:
                results.append(t)
        except Exception:
            pass
    return results
