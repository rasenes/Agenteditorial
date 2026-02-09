from __future__ import annotations

from ..core.logger import get_logger
from ..providers import router

logger = get_logger(__name__)


class Translator:
    async def to_french(self, text: str, source_language: str) -> str:
        if source_language == "fr":
            return text

        prompt = (
            "Translate this text into natural French for social media. "
            "Keep meaning, keep impact, no markdown.\n\n"
            f"Source language: {source_language}\n"
            f"Text: {text}"
        )
        try:
            result = await router.generate(prompt)
            return result.text.strip() or text
        except Exception as exc:  # noqa: BLE001
            logger.warning("Translation fallback used: %s", exc)
            return text


translator = Translator()
