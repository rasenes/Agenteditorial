from __future__ import annotations

from dataclasses import dataclass

from ..core.config import SETTINGS


@dataclass
class OllamaClient:
    base_url: str = SETTINGS.ollama.base_url
    model: str = SETTINGS.ollama.model
    temperature: float = SETTINGS.ollama.temperature

    async def healthcheck(self, timeout: float = 3.0) -> bool:
        try:
            import httpx
        except Exception:  # noqa: BLE001
            return False

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:  # noqa: BLE001
            return False

    async def generate(self, prompt: str, timeout: float) -> str:
        try:
            import httpx
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("httpx package missing") from exc

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return str(data.get("response", "")).strip()
