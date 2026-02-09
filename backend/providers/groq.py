from __future__ import annotations

from dataclasses import dataclass

from ..core.config import SETTINGS


@dataclass
class GroqClient:
    api_key: str = SETTINGS.groq.api_key
    model: str = SETTINGS.groq.model
    temperature: float = SETTINGS.groq.temperature

    async def healthcheck(self, timeout: float = 3.0) -> bool:
        return bool(self.api_key)

    async def generate(self, prompt: str, timeout: float) -> str:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY missing")
        try:
            from groq import AsyncGroq
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("groq package missing") from exc

        client = AsyncGroq(api_key=self.api_key, timeout=timeout)
        completion = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You generate concise, high-quality social posts."},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
        )
        return (completion.choices[0].message.content or "").strip()
