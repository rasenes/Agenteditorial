"""
Moteur Remix pour transformer les tweets.
Raccourcir, aggresser, ironiser, minimaliser, etc.
"""

from typing import List, Optional
import asyncio

from ..core.logger import get_logger
from ..core.utils import truncate_text, validate_tweet, clean_text
from ..models.tweet import Tweet
from ..providers.router import router

logger = get_logger(__name__)


class RemixEngine:
    """Transforme les tweets de multiples façons (remix)."""
    
    REMIX_STYLES = {
        "short": {
            "description": "ultra-court (< 100 chars)",
            "prompt": "Réécrivez ce tweet en moins de 100 caractères, garde le message clé mais sois extrêmement concis."
        },
        "aggressive": {
            "description": "version agressive et provocante",
            "prompt": "Réécrivez ce tweet de manière plus agressive, directe et provocante, mais respectueux."
        },
        "irony": {
            "description": "version ironique et spirituelle",
            "prompt": "Réécrivez ce tweet avec beaucoup d'ironie et d'humour."
        },
        "question": {
            "description": "version sous forme de question",
            "prompt": "Réécrivez ce tweet en forme de question intrigante."
        },
        "data": {
            "description": "version avec stat ou chiffre",
            "prompt": "Réécrivez ce tweet en incluant un chiffre ou une statistique."
        },
        "hook": {
            "description": "version avec un hook accrocheur",
            "prompt": "Réécrivez ce tweet pour commencer par un hook très accrocheur et captivant."
        },
    }
    
    def __init__(self):
        self.router = router
    
    async def remix(self, tweet: Tweet, style: str = "short") -> Optional[Tweet]:
        """
        Remixe un tweet dans un style donné.
        
        Args:
            tweet: Tweet original
            style: Style de remix
        
        Returns:
            Tweet remixé ou None si erreur
        """
        if style not in self.REMIX_STYLES:
            logger.warning(f"Unknown remix style: {style}, using 'short'")
            style = "short"
        
        style_info = self.REMIX_STYLES[style]
        
        prompt = f"""Original tweet:
"{tweet.content}"

Instructions: {style_info['prompt']}

Provide only the remixed tweet, no explanation."""
        
        try:
            remixed = await self.router.generate(prompt, temperature=0.8, max_tokens=300)
            remixed = clean_text(remixed)
            
            is_valid, msg = validate_tweet(remixed)
            if not is_valid:
                logger.warning(f"Remixed tweet invalid: {msg}")
                return None
            
            return Tweet(
                content=remixed,
                theme=tweet.theme,
                language=tweet.language,
                source=f"remixed-{style}",
                metadata={
                    "original_content": tweet.content,
                    "remix_style": style,
                },
            )
        except Exception as e:
            logger.error(f"Remix failed: {e}")
            return None
    
    async def remix_batch(self, tweets: List[Tweet], styles: List[str] = None) -> List[Tweet]:
        """
        Remixe plusieurs tweets avec différents styles.
        
        Args:
            tweets: Tweets à remixer
            styles: Styles à utiliser (list or all)
        
        Returns:
            Tous les tweets remixés
        """
        if styles is None:
            styles = list(self.REMIX_STYLES.keys())
        
        remixed_tweets = []
        
        for tweet in tweets:
            for style in styles:
                remixed = await self.remix(tweet, style)
                if remixed:
                    remixed_tweets.append(remixed)
        
        return remixed_tweets
    
    async def remix_parallel(self, tweet: Tweet) -> List[Tweet]:
        """
        Crée plusieurs remixes du même tweet en parallèle.
        
        Args:
            tweet: Tweet à remixer
        
        Returns:
            Tous les remixes
        """
        tasks = [
            self.remix(tweet, style)
            for style in self.REMIX_STYLES.keys()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=False)
        return [r for r in results if r is not None]


# Instance globale
remix_engine = RemixEngine()
