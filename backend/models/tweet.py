from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from ..core.utils import normalize_text

THEMES = [
    "IA",
    "Tech",
    "Science",
    "Sport",
    "Politique",
    "Business",
    "Crypto",
    "Univers",
    "Culture",
    "Humour",
    "Faits surprenants",
    "Philosophie",
    "Futur",
]

STYLES = ["insight", "agressive", "ironique", "minimal", "story", "data"]


class ScoreBreakdown(BaseModel):
    length: float = 0.0
    clarity: float = 0.0
    emotion: float = 0.0
    mirror: float = 0.0
    punchline: float = 0.0
    contradiction: float = 0.0
    viral: float = 0.0
    total: float = 0.0


class TweetCandidate(BaseModel):
    id: str
    text: str = Field(min_length=8, max_length=280)
    theme: str
    style: str
    language: str = "fr"
    angle: str = "standard"
    source_trend_id: str | None = None
    provider_used: str = "fallback"
    score: float = 0.0
    breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)

    @field_validator("text")
    @classmethod
    def _normalize(cls, value: str) -> str:
        return normalize_text(value)


class TweetRemixSet(BaseModel):
    original: TweetCandidate
    shorter: TweetCandidate
    aggressive: TweetCandidate
    ironic: TweetCandidate
    minimalist: TweetCandidate
    punchline: TweetCandidate


class GenerateTweetsRequest(BaseModel):
    trend_id: str | None = None
    trend_text: str | None = None
    theme: str = "IA"
    style: str = "insight"
    language: Literal["en", "fr", "es", "de"] = "fr"
    count: int = Field(default=9, ge=3, le=30)
    include_remix: bool = True
    draft_mode: bool = False


class GenerateTweetsResponse(BaseModel):
    top3: list[TweetCandidate]
    all_candidates: list[TweetCandidate]
    remixes: list[TweetRemixSet] = Field(default_factory=list)
    metadata: dict


class ABTestRequest(BaseModel):
    theme: str
    trend_text: str
    variant_a_style: str = "insight"
    variant_b_style: str = "ironique"
    samples: int = Field(default=6, ge=2, le=20)


class ABTestResult(BaseModel):
    winner: str
    variant_a_avg_score: float
    variant_b_avg_score: float
    variant_a_top: list[TweetCandidate]
    variant_b_top: list[TweetCandidate]


class FavoriteTweetRequest(BaseModel):
    tweet_id: str
