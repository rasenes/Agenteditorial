from __future__ import annotations

from ..core.utils import estimate_tweet_length, short_hash
from ..models.tweet import TweetCandidate, TweetRemixSet


class RemixEngine:
    def remix(self, tweet: TweetCandidate) -> TweetRemixSet:
        shorter = self._make_candidate(tweet, self._shorten(tweet.text), "minimal")
        aggressive = self._make_candidate(tweet, self._aggressive(tweet.text), "agressive")
        ironic = self._make_candidate(tweet, self._ironic(tweet.text), "ironique")
        minimalist = self._make_candidate(tweet, self._minimal(tweet.text), "minimal")
        punchline = self._make_candidate(tweet, self._punchline(tweet.text), "story")

        return TweetRemixSet(
            original=tweet,
            shorter=shorter,
            aggressive=aggressive,
            ironic=ironic,
            minimalist=minimalist,
            punchline=punchline,
        )

    def _make_candidate(self, origin: TweetCandidate, text: str, style: str) -> TweetCandidate:
        clipped = text.strip()
        if estimate_tweet_length(clipped) > 280:
            clipped = clipped[:277] + "..."
        return TweetCandidate(
            id=f"rmx-{short_hash(origin.id + clipped)}",
            text=clipped,
            theme=origin.theme,
            style=style,
            language=origin.language,
            angle=origin.angle,
            source_trend_id=origin.source_trend_id,
            provider_used=origin.provider_used,
        )

    def _shorten(self, text: str) -> str:
        if len(text) < 120:
            return text
        chunks = text.split(" ")
        return " ".join(chunks[: max(12, int(len(chunks) * 0.55))])

    def _aggressive(self, text: str) -> str:
        base = text.rstrip(".!")
        return f"Arrêtons l’hypocrisie: {base}. C’est maintenant qu’il faut agir."  # noqa: RUF001

    def _ironic(self, text: str) -> str:
        return f"Bien sûr, tout est sous contrôle... sauf que {text[:180].lower()}"

    def _minimal(self, text: str) -> str:
        words = text.split()
        return " ".join(words[:14]) + ("." if len(words) > 14 else "")

    def _punchline(self, text: str) -> str:
        return f"{text.rstrip('.')} ? Voilà le vrai sujet."


remix_engine = RemixEngine()
