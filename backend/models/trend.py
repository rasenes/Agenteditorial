from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from ..core.utils import normalize_text


class Trend(BaseModel):
    id: str
    title: str = Field(min_length=4, max_length=240)
    summary: str = Field(default="", max_length=600)
    source: str
    source_url: str = ""
    language: str = "en"
    theme: str = "IA"
    momentum: float = 0.0
    viral_angle: str = "standard"
    tags: list[str] = Field(default_factory=list)
    created_at: float

    @field_validator("title", "summary")
    @classmethod
    def _clean(cls, value: str) -> str:
        return normalize_text(value)


class TrendFetchResponse(BaseModel):
    trends: list[Trend]
    count: int
    fetched_at: float


class TrendAnalyzeResponse(BaseModel):
    trend: Trend
    detected_angles: list[str]
    reason: str
