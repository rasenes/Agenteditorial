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
                response.raise_for_status()
                payload = response.json()
        except Exception:  # noqa: BLE001
            return False

        models = [m.get("name", "") for m in payload.get("models", []) if isinstance(m, dict)]
        if not models:
            return True

        wanted = (self.model or "").strip().lower()
        if not wanted:
            return True

        for name in models:
            name_lower = str(name).lower()
            if name_lower == wanted:
                return True
            if name_lower.startswith(wanted + ":"):
                return True
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
            "options": {
                "temperature": self.temperature,
                # Limit generation to keep latency bounded.
                "num_predict": 700,
            },
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            if response.status_code >= 400:
                raise RuntimeError(f"Ollama error {response.status_code}: {response.text[:400]}")
            data = response.json()
            return str(data.get("response", "")).strip()
