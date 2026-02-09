from __future__ import annotations

from dataclasses import dataclass

from ..core.config import SETTINGS
from ..core.logger import get_logger
from ..core.utils import async_retry
from .groq import GroqClient
from .ollama import OllamaClient
from .openai import OpenAIClient

logger = get_logger(__name__)


@dataclass
class LLMResult:
    text: str
    provider: str


class LLMRouter:
    def __init__(self) -> None:
        self._clients = {
            "ollama": OllamaClient(),
            "openai": OpenAIClient(),
            "groq": GroqClient(),
        }

    def _provider_chain(self) -> list[str]:
        preferred = SETTINGS.llm.primary_provider
        configured = [p for p in SETTINGS.llm.fallback_order if p in self._clients]
        if preferred in configured:
            configured.remove(preferred)
            return [preferred] + configured
        return configured

    async def generate(self, prompt: str) -> LLMResult:
        last_error: Exception | None = None

        for provider_name in self._provider_chain():
            client = self._clients[provider_name]
            try:
                if not await client.healthcheck(timeout=3.0):
                    logger.warning("Provider unavailable: %s", provider_name)
                    continue

                text = await async_retry(
                    client.generate,
                    prompt,
                    timeout=SETTINGS.llm.request_timeout_sec,
                    retries=SETTINGS.llm.max_retries,
                    delay=0.4,
                )
                if text:
                    return LLMResult(text=text, provider=provider_name)

            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning("Provider %s failed: %r", provider_name, exc)

        raise RuntimeError(
            "No LLM available. "
            "If you use Ollama: install a model (ex: `ollama pull llama3`) and set OLLAMA_MODEL if needed. "
            "Or set OPENAI_API_KEY / GROQ_API_KEY. "
            f"Last error: {last_error!r}"
        )


router = LLMRouter()
