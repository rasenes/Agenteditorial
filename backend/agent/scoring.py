from __future__ import annotations

import re

from ..core.utils import clamp, estimate_tweet_length
from ..models.tweet import ScoreBreakdown, TweetCandidate


class TweetScoringEngine:
    EMOTION_WORDS = {
        "urgent",
        "explose",
        "incroyable",
        "secret",
        "scandale",
        "choc",
        "jamais",
        "révolution",
        "alerte",
        "bascule",
    }
    MIRROR_WORDS = {"tu", "vous", "ton", "votre", "on", "nous"}

    def score(self, tweet: TweetCandidate) -> TweetCandidate:
        text = tweet.text
        length = self._score_length(text)
        clarity = self._score_clarity(text)
        emotion = self._score_emotion(text)
        mirror = self._score_mirror(text)
        punchline = self._score_punchline(text)
        contradiction = self._score_contradiction(text)
        viral = self._score_viral(text)

        total = (
            0.14 * length
            + 0.16 * clarity
            + 0.15 * emotion
            + 0.10 * mirror
            + 0.15 * punchline
            + 0.15 * contradiction
            + 0.15 * viral
        )

        tweet.breakdown = ScoreBreakdown(
            length=length,
            clarity=clarity,
            emotion=emotion,
            mirror=mirror,
            punchline=punchline,
            contradiction=contradiction,
            viral=viral,
            total=round(total, 4),
        )
        tweet.score = round(total, 4)
        return tweet

    def rank(self, tweets: list[TweetCandidate]) -> list[TweetCandidate]:
        scored = [self.score(t) for t in tweets]
        return sorted(scored, key=lambda t: t.score, reverse=True)

    def _score_length(self, text: str) -> float:
        ln = estimate_tweet_length(text)
        if 120 <= ln <= 220:
            return 1.0
        if 80 <= ln < 120 or 220 < ln <= 260:
            return 0.8
        if 40 <= ln < 80 or 260 < ln <= 280:
            return 0.55
        return 0.25

    def _score_clarity(self, text: str) -> float:
        sentence_count = max(1, len([s for s in re.split(r"[.!?]", text) if s.strip()]))
        punctuation_noise = len(re.findall(r"[!?]{2,}|\.{3,}", text))
        base = 1.0 - (0.12 * max(0, sentence_count - 2)) - (0.08 * punctuation_noise)
        return clamp(base)

    def _score_emotion(self, text: str) -> float:
        tokens = re.findall(r"\w+", text.lower())
        hits = sum(1 for token in tokens if token in self.EMOTION_WORDS)
        has_exclaim = "!" in text
        base = 0.42 + (hits * 0.13) + (0.08 if has_exclaim else 0.0)
        return clamp(base)

    def _score_mirror(self, text: str) -> float:
        tokens = set(re.findall(r"\w+", text.lower()))
        hits = len(tokens & self.MIRROR_WORDS)
        if hits == 0:
            return 0.35
        if hits == 1:
            return 0.75
        if hits <= 3:
            return 0.9
        return 0.65

    def _score_punchline(self, text: str) -> float:
        end_bonus = 0.2 if re.search(r"[!?]$", text.strip()) else 0.0
        has_colon = 0.15 if ":" in text else 0.0
        short_end = 0.2 if len(text.split()) <= 24 else 0.0
        return clamp(0.35 + end_bonus + has_colon + short_end)

    def _score_contradiction(self, text: str) -> float:
        markers = ["mais", "pourtant", "alors que", "sauf que", "paradoxalement", "contre-intuitif"]
        hits = sum(1 for marker in markers if marker in text.lower())
        return clamp(0.25 + hits * 0.22)

    def _score_viral(self, text: str) -> float:
        hashtags = len(re.findall(r"#\w+", text))
        numbers = len(re.findall(r"\d+", text))
        question = 1 if "?" in text else 0
        base = 0.4 + min(hashtags * 0.08, 0.2) + min(numbers * 0.08, 0.16) + question * 0.12
        return clamp(base)


scoring_engine = TweetScoringEngine()
