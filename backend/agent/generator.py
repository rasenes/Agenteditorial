from __future__ import annotations

import asyncio
import json
from typing import Any

from ..core.config import SETTINGS
from ..core.logger import get_logger
from ..core.utils import normalize_text, parse_json_loose, short_hash
from ..models.tweet import GenerateTweetsRequest, TweetCandidate
from ..models.trend import Trend
from ..providers import router
from .memory_engine import memory_engine
from .translator import translator

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

    async def generate_candidates(self, request: GenerateTweetsRequest, trend: Trend) -> list[TweetCandidate]:
        per_batch = max(3, request.count // 3)
        prompts = [
            self._build_prompt(request=request, trend=trend, n=per_batch, seed=idx)
            for idx in range(3)
        ]

        semaphore = asyncio.Semaphore(SETTINGS.generation.max_parallel_generations)

        async def run_prompt(prompt: str) -> tuple[str, str]:
            async with semaphore:
                try:
                    result = await router.generate(prompt)
                    return result.text, result.provider
                except Exception as exc:  # noqa: BLE001
                    logger.warning("LLM generation failed, fallback in use: %s", exc)
                    return self._fallback_payload(prompt, per_batch), "fallback"

        outputs = await asyncio.gather(*(run_prompt(prompt) for prompt in prompts), return_exceptions=False)

        candidates: list[TweetCandidate] = []
        for text, provider in outputs:
            candidates.extend(self._to_candidates(raw=text, provider=provider, request=request, trend=trend))

        deduped = self._dedupe(candidates)
        final = deduped[: request.count]

        if request.language != "fr":
            await self._translate_candidates(final, request.language)

        return final

    def _build_prompt(self, request: GenerateTweetsRequest, trend: Trend, n: int, seed: int) -> str:
        tone = self.THEME_TONE.get(request.theme, "direct")
        avoid = memory_engine.get_similar_texts(trend.title, threshold=0.7)[:4]

        avoid_block = "\n".join(f"- {line}" for line in avoid) if avoid else "- Aucun"
        return (
            "Tu es un agent éditorial expert des tweets viraux.\n"
            f"Thème: {request.theme}\n"
            f"Style: {request.style}\n"
            f"Angle viral principal: {trend.viral_angle}\n"
            f"Ton éditorial: {tone}\n"
            f"Sujet: {trend.title}\n"
            f"Contexte: {trend.summary}\n"
            f"Langue de sortie: {request.language}\n"
            f"Nombre de tweets: {n}\n"
            f"Seed créative: {seed}\n"
            "Contraintes strictes:\n"
            "- 280 caractères maximum\n"
            "- 1 idée forte par tweet\n"
            "- pas de markdown\n"
            "- pas de guillemets autour des phrases\n"
            "- si possible, inclure un contraste, un chiffre, ou une punchline\n"
            "- éviter les répétitions avec ces exemples historiques:\n"
            f"{avoid_block}\n\n"
            "Réponds en JSON strict sous forme de tableau:"
            " [{\"text\":\"...\",\"angle\":\"...\"}]"
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
            candidate = TweetCandidate(
                id=f"tw-{short_hash(text + trend.id)}",
                text=text,
                theme=request.theme,
                style=request.style,
                language="fr",
                angle=str(row.get("angle", trend.viral_angle))[:40],
                source_trend_id=trend.id,
                provider_used=provider,
            )
            candidates.append(candidate)
        return candidates

    async def _translate_candidates(self, candidates: list[TweetCandidate], source_language: str) -> None:
        for candidate in candidates:
            candidate.text = await translator.to_french(candidate.text, source_language)
            candidate.language = "fr"

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

    def _fallback_payload(self, prompt: str, n: int) -> str:
        topic = "actualité"
        for line in prompt.splitlines():
            if line.startswith("Sujet:"):
                topic = line.replace("Sujet:", "").strip()
                break
        rows = [
            {
                "text": f"{topic}: ce n'est pas juste une news, c'est un signal faible qui va redéfinir le débat des 12 prochains mois.",
                "angle": "insight",
            },
            {
                "text": f"Tout le monde regarde {topic}, peu voient l'effet secondaire: le vrai gagnant sera celui qui agit avant la foule.",
                "angle": "contradiction",
            },
            {
                "text": f"{topic} prouve une chose: quand le rythme accélère, l'inaction devient une décision risquée.",
                "angle": "urgence",
            },
        ]
        return json.dumps(rows[:n], ensure_ascii=False)


generator = TweetGenerator()
