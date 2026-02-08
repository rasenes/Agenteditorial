"""
Traducteur multilingue.
Support : EN, FR, ES, DE avec traduction naturelle.
"""

from typing import Optional

from ..core.logger import get_logger
from ..providers.router import router

logger = get_logger(__name__)


class Translator:
    """Traduit des textes entre langues."""
    
    SUPPORTED_LANGS = {
        "fr": "French",
        "en": "English",
        "es": "Spanish",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
    }
    
    def __init__(self):
        self.router = router
    
    async def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "fr",
        keep_tone: bool = True,
    ) -> Optional[str]:
        """Traduit un texte."""
        if source_lang == target_lang:
            return text
        
        if source_lang not in self.SUPPORTED_LANGS:
            logger.warning(f"Unsupported source language: {source_lang}")
            return None
        
        if target_lang not in self.SUPPORTED_LANGS:
            logger.warning(f"Unsupported target language: {target_lang}")
            return None
        
        source_name = self.SUPPORTED_LANGS[source_lang]
        target_name = self.SUPPORTED_LANGS[target_lang]
        
        tone_instruction = "Keep the exact tone, style, and any humor or irony. Don't change the meaning." if keep_tone else ""
        
        prompt = f"""Translate this text from {source_name} to {target_name}.
        
Text to translate:
"{text}"

{tone_instruction}

Provide ONLY the translation, no explanation."""
        
        try:
            translated = await self.router.generate(prompt, temperature=0.3, max_tokens=300)
            return translated.strip()
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return None
    
    async def translate_batch(
        self,
        texts: list[str],
        source_lang: str = "en",
        target_lang: str = "fr",
    ) -> list[Optional[str]]:
        """Traduit plusieurs textes."""
        import asyncio
        
        tasks = [
            self.translate(text, source_lang, target_lang)
            for text in texts
        ]
        
        return await asyncio.gather(*tasks)
    
    async def detect_language(self, text: str) -> str:
        """Détecte la langue d'un texte."""
        try:
            # Utilise une libraire légère pour la détection
            from langdetect import detect
            lang_code = detect(text)
            
            # Normalise
            for code, name in self.SUPPORTED_LANGS.items():
                if lang_code.startswith(code):
                    return code
            
            return "en"  # Default
        except Exception:
            # Fallback simple : count French words
            fr_words = ["le", "la", "les", "de", "un", "une", "est", "et", "que", "pour"]
            fr_count = sum(1 for word in text.lower().split() if word in fr_words)
            
            return "fr" if fr_count > len(text.split()) * 0.1 else "en"


# Instance globale
translator = Translator()
