def remix_question(tweet: str) -> str:
    if "?" in tweet:
        return tweet
    return tweet + " Vraiment ?"


def remix_contrast(tweet: str) -> str:
    return f"Tout le monde regarde ailleurs.\n{tweet}"


def remix_silence(tweet: str) -> str:
    return tweet.replace(".", "").strip()


REMIXERS = [
    remix_question,
    remix_contrast,
    remix_silence,
]


def remix(tweet: str) -> list[str]:
    remixed = []
    for fn in REMIXERS:
        try:
            t = fn(tweet)
            if t and t != tweet:
                remixed.append(t)
        except Exception:
            pass
    return remixed
