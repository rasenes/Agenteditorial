from __future__ import annotations

import json
from typing import Any

from ..core.config import SETTINGS
from ..core.logger import get_logger
from ..core.utils import normalize_text, parse_json_loose, short_hash
from ..models.tweet import GenerateTweetsRequest, TweetCandidate
from ..models.trend import Trend
from ..providers import router
from .memory_engine import memory_engine

logger = get_logger(__name__)


class TweetGenerator:
    THEME_TONE: dict[str, str] = {
        "IA": "visionnaire, concret, lucide",
        "Tech": "analytique et direct",
        "Science": "pédagogique mais percutant",
        "Sport": "énergique, compétitif",
        "Politique": "tranché, argumenté",
        "Business": "stratégique, orienté résultats",
        "Crypto": "audacieux, orienté risque",
        "Univers": "émerveillé, précis",
        "Culture": "narratif et sensoriel",
        "Humour": "drôle, sec, mémorable",
        "Faits surprenants": "curieux et punchy",
        "Philosophie": "réflexif, paradoxal",
        "Futur": "prospectif, concret",
    }

    ALLOWED_ANGLES = {"insight", "contradiction", "question", "punchline", "data", "ironie", "urgence", "surprise"}

    async def generate_candidates(self, request: GenerateTweetsRequest, trend: Trend) -> list[TweetCandidate]:
        prompt = self._build_prompt(request=request, trend=trend, n=request.count)
        result = await router.generate(prompt)

        candidates = self._to_candidates(raw=result.text, provider=result.provider, request=request, trend=trend)
        if not candidates:
            raise RuntimeError("LLM returned no usable tweets")

        deduped = self._dedupe(candidates)
        if len(deduped) < request.count:
            deduped.extend(self._fallback_candidates(trend=trend, request=request, missing=request.count - len(deduped)))

        return deduped[: request.count]

    def _build_prompt(self, request: GenerateTweetsRequest, trend: Trend, n: int) -> str:
        tone = self.THEME_TONE.get(request.theme, "direct")
        avoid = memory_engine.get_similar_texts(trend.title, threshold=0.7)[:4]
        avoid_block = "\n".join(f"- {line}" for line in avoid) if avoid else "- Aucun"

        return (
            "Tu es un ghostwriter FR expert en tweets viraux.\n"
            "Tu ecris UNIQUEMENT en francais naturel (pas une traduction).\n\n"
            f"Theme: {request.theme}\n"
            f"Style: {request.style}\n"
            f"Angle viral principal: {trend.viral_angle}\n"
            f"Ton editorial: {tone}\n"
            f"Sujet: {trend.title}\n"
            f"Contexte: {trend.summary}\n"
            f"Nombre de tweets: {n}\n\n"
            "Contraintes strictes:\n"
            "- 280 caracteres maximum\n"
            "- 1 idee forte par tweet\n"
            "- pas de markdown\n"
            "- pas de guillemets autour des phrases\n"
            "- concret, specifique, avec un twist\n"
            "- 0 a 2 hashtags MAX et seulement si pertinents\n"
            "- ne PAS ajouter #IA si le sujet n'est pas l'IA\n"
            "- angle OBLIGATOIRE dans cette liste: insight, contradiction, question, punchline, data, ironie, urgence, surprise\n"
            "- eviter les repetitions avec ces exemples historiques:\n"
            f"{avoid_block}\n\n"
            "Reponds UNIQUEMENT en JSON strict (tableau) :"
            " [{\"text\":\"...\",\"angle\":\"insight|contradiction|question|punchline|data|ironie|urgence|surprise\"}]"
        )

    def _to_candidates(
        self,
        raw: str,
        provider: str,
        request: GenerateTweetsRequest,
        trend: Trend,
    ) -> list[TweetCandidate]:
        payload: Any = parse_json_loose(raw)
        rows: list[dict[str, Any]] = []

        if isinstance(payload, list):
            rows = [row for row in payload if isinstance(row, dict) and row.get("text")]
        elif isinstance(payload, dict) and isinstance(payload.get("tweets"), list):
            rows = [row for row in payload["tweets"] if isinstance(row, dict) and row.get("text")]

        if not rows:
            rows = [{"text": line.strip(), "angle": trend.viral_angle} for line in raw.split("\n") if len(line.strip()) > 12]

        candidates: list[TweetCandidate] = []
        for row in rows:
            text = normalize_text(str(row.get("text", "")))
            if not text:
                continue
            if len(text) > 280:
                text = text[:277] + "..."

            angle = str(row.get("angle", trend.viral_angle)).strip().lower()
            if angle not in self.ALLOWED_ANGLES:
                angle = trend.viral_angle

            candidates.append(
                TweetCandidate(
                    id=f"tw-{short_hash(text + trend.id)}",
                    text=text,
                    theme=request.theme,
                    style=request.style,
                    language="fr",
                    angle=angle[:40],
                    source_trend_id=trend.id,
                    provider_used=provider,
                )
            )

        return candidates

    def _dedupe(self, tweets: list[TweetCandidate]) -> list[TweetCandidate]:
        seen: set[str] = set()
        deduped: list[TweetCandidate] = []
        for tweet in tweets:
            key = short_hash(tweet.text)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(tweet)
        return deduped

    def _fallback_candidates(self, trend: Trend, request: GenerateTweetsRequest, missing: int) -> list[TweetCandidate]:
        base = [
            {
                "text": f"{trend.title}: ce n'est pas juste une news, c'est un signal faible qui va reconfigurer les priorites. Et peu de gens le voient venir.",
                "angle": "insight",
            },
            {
                "text": f"Tout le monde parle de {trend.title}. Le vrai sujet, c'est l'effet secondaire. Celui qui le comprend maintenant aura 6 mois d'avance.",
                "angle": "contradiction",
            },
            {
                "text": f"{trend.title} pose une question simple: tu veux avoir raison plus tard, ou agir pendant que c'est encore possible ?",
                "angle": "question",
            },
        ]
        rows = base[:missing]
        raw = json.dumps(rows, ensure_ascii=False)
        return self._to_candidates(raw=raw, provider="fallback", request=request, trend=trend)


generator = TweetGenerator()
