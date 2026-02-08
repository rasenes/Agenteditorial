"""
Router intelligent pour les providers LLM.
Support : Ollama, OpenAI, Groq avec fallback automatique.
"""

import asyncio
from typing import Optional, List
from enum import Enum

from ..core.config import CONFIG
from ..core.logger import get_logger
from ..core.utils import async_retry, extract_json

logger = get_logger(__name__)


class ProviderType(str, Enum):
    """Types de providers disponibles."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    GROQ = "groq"


class LLMProvider:
    """Interface abstraite pour providers LLM."""
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Génère du texte."""
        raise NotImplementedError
    
    async def is_available(self) -> bool:
        """Vérifie la disponibilité du provider."""
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    """Provider Ollama local."""
    
    def __init__(self):
        self.base_url = CONFIG.ollama.base_url
        self.model = CONFIG.ollama.model
        self.temperature = CONFIG.ollama.temperature
        self.timeout = CONFIG.ollama.timeout
    
    @async_retry(max_attempts=2, delay=1.0, exceptions=(Exception,))
    async def generate(self, prompt: str, **kwargs) -> str:
        """Génère du texte via Ollama."""
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "temperature": kwargs.get("temperature", self.temperature),
                        "stream": False,
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "").strip()
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    async def is_available(self) -> bool:
        """Vérifie si Ollama est disponible."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False


class OpenAIProvider(LLMProvider):
    """Provider OpenAI."""
    
    def __init__(self):
        self.api_key = CONFIG.openai.api_key
        self.model = CONFIG.openai.model
        self.temperature = CONFIG.openai.temperature
        self.timeout = CONFIG.openai.timeout
    
    @async_retry(max_attempts=2, delay=1.0, exceptions=(Exception,))
    async def generate(self, prompt: str, **kwargs) -> str:
        """Génère du texte via OpenAI."""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.api_key)
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", 500),
                timeout=self.timeout,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def is_available(self) -> bool:
        """Vérifie si OpenAI est disponible."""
        return bool(self.api_key)


class GroqProvider(LLMProvider):
    """Provider Groq."""
    
    def __init__(self):
        self.api_key = CONFIG.groq.api_key
        self.model = CONFIG.groq.model
        self.temperature = CONFIG.groq.temperature
        self.timeout = CONFIG.groq.timeout
    
    @async_retry(max_attempts=2, delay=1.0, exceptions=(Exception,))
    async def generate(self, prompt: str, **kwargs) -> str:
        """Génère du texte via Groq."""
        try:
            from groq import AsyncGroq
            
            client = AsyncGroq(api_key=self.api_key)
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", 500),
                timeout=self.timeout,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise
    
    async def is_available(self) -> bool:
        """Vérifie si Groq est disponible."""
        return bool(self.api_key)


class LLMRouter:
    """
    Router intelligent pour les providers LLM.
    Gère fallback, retry, et sélection dynamique.
    """
    
    def __init__(self):
        self.providers: dict[str, LLMProvider] = {
            ProviderType.OLLAMA: OllamaProvider(),
            ProviderType.OPENAI: OpenAIProvider(),
            ProviderType.GROQ: GroqProvider(),
        }
        self.primary = CONFIG.llm.provider
        self.fallback_order = self._build_fallback_order()
    
    def _build_fallback_order(self) -> List[str]:
        """Crée l'ordre de fallback basé sur la config."""
        order = [self.primary]
        
        # Ajoute les autres providers
        for provider_type in ProviderType:
            if provider_type.value != self.primary:
                order.append(provider_type.value)
        
        return order
    
    async def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        fallback: bool = True,
    ) -> str:
        """
        Génère du texte avec fallback automatique.
        
        Args:
            prompt: Prompt pour le LLM
            temperature: Temperature (override config)
            max_tokens: Max tokens (override config)
            fallback: Utiliser le fallback si provider primaire échoue
        
        Returns:
            Texte généré
        """
        kwargs = {}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        
        providers_to_try = self.fallback_order if fallback else [self.primary]
        last_error = None
        
        for provider_name in providers_to_try:
            try:
                provider = self.providers.get(provider_name)
                if not provider:
                    continue
                
                # Vérifie disponibilité
                if not await provider.is_available():
                    logger.warning(f"Provider {provider_name} not available")
                    continue
                
                logger.info(f"Generating with {provider_name}")
                result = await provider.generate(prompt, **kwargs)
                return result
            
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Generation with {provider_name} failed: {e}, "
                    f"trying next provider..."
                )
                continue
        
        # Tous les providers ont échoué
        error_msg = f"All providers exhausted. Last error: {last_error}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    async def generate_batch(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[str]:
        """
        Génère en parallèle pour plusieurs prompts.
        
        Args:
            prompts: Liste de prompts
            **kwargs: Arguments pour generate()
        
        Returns:
            Liste de textes générés
        """
        tasks = [self.generate(prompt, **kwargs) for prompt in prompts]
        return await asyncio.gather(*tasks, return_exceptions=False)


# Instance globale
router = LLMRouter()
