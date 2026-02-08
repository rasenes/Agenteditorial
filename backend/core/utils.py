"""
Utilitaires générales : parsing, validation, formatage, retry logic.
"""

import asyncio
import time
from typing import Any, Callable, Optional, TypeVar, Coroutine
from functools import wraps
import json
from datetime import datetime

from .logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Décorateur retry avec backoff exponentiel.
    
    Args:
        max_attempts: Nombre max de tentatives
        delay: Délai initial en secondes
        backoff: Multiplicateur de délai
        exceptions: Tuple d'exceptions à retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"Retry exhausted for {func.__name__}: {e}")
                        raise
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}), "
                        f"retrying in {current_delay}s: {e}"
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
        
        return wrapper
    return decorator


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Décorateur retry async."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"Async retry exhausted for {func.__name__}: {e}")
                        raise
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}), "
                        f"retrying in {current_delay}s: {e}"
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        
        return wrapper
    return decorator


def extract_json(text: str) -> Optional[dict]:
    """
    Extrait du JSON d'une réponse LLM.
    Gère les cas où le JSON est wrappé dans du markdown.
    
    Args:
        text: Texte contenant potentiellement du JSON
    
    Returns:
        Dict si JSON trouvé, None sinon
    """
    text = text.strip()
    
    # Essaie directement
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Recherche ```json ... ```
    start = text.find("```json")
    if start != -1:
        start += 7
        end = text.find("```", start)
        if end != -1:
            try:
                return json.loads(text[start:end].strip())
            except json.JSONDecodeError:
                pass
    
    # Recherche ```  ... ```
    start = text.find("```")
    if start != -1:
        start += 3
        end = text.find("```", start)
        if end != -1:
            try:
                return json.loads(text[start:end].strip())
            except json.JSONDecodeError:
                pass
    
    # Recherche { ... }
    start = text.find("{")
    if start != -1:
        end = text.rfind("}")
        if end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass
    
    return None


def truncate_text(text: str, max_length: int = 280) -> str:
    """
    Tronque un texte à une longueur max.
    Préserve les mots complets.
    
    Args:
        text: Texte à tronquer
        max_length: Longueur max
    
    Returns:
        Texte tronqué avec ellipsis si nécessaire
    """
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length-3]
    
    # Trouve le dernier espace
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.7:  # Si espace trouvé dans les 70% premiers
        truncated = truncated[:last_space]
    
    return truncated + "..."


def clean_text(text: str) -> str:
    """
    Nettoie le texte : trim, normalise whitespace, etc.
    
    Args:
        text: Texte à nettoyer
    
    Returns:
        Texte nettoyé
    """
    # Trim
    text = text.strip()
    
    # Normalise les espaces multiples
    text = ' '.join(text.split())
    
    # Supprime les caractères de contrôle
    text = ''.join(c for c in text if c.isprintable() or c in '\n\t')
    
    return text


def estimate_tweet_length(text: str) -> int:
    """
    Estime la longueur d'un tweet (compte les URLs comme 23 caractères).
    
    Args:
        text: Texte du tweet
    
    Returns:
        Longueur estimée
    """
    import re
    
    length = len(text)
    
    # URLs sont comptées comme 23 caractères
    urls = re.findall(r'https?://\S+', text)
    if urls:
        url_chars = sum(len(url) for url in urls)
        length = length - url_chars + (len(urls) * 23)
    
    return length


def validate_tweet(text: str) -> tuple[bool, str]:
    """
    Valide un tweet.
    
    Args:
        text: Texte du tweet
    
    Returns:
        (is_valid, message)
    """
    text = text.strip()
    
    if not text:
        return False, "Tweet vide"
    
    length = estimate_tweet_length(text)
    
    if length > 280:
        return False, f"Tweet trop long: {length}/280"
    
    if length < 10:
        return False, "Tweet trop court (<10 chars)"
    
    return True, "OK"


def format_timestamp(ts: Optional[float] = None) -> str:
    """Formate un timestamp en string lisible."""
    if ts is None:
        ts = time.time()
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def safe_json_dumps(obj: Any) -> str:
    """JSON dumps safe avec gestion des erreurs."""
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        logger.error(f"JSON dumps failed: {e}")
        return str(obj)


def safe_json_loads(text: str) -> Optional[Any]:
    """JSON loads safe avec gestion des erreurs."""
    try:
        return json.loads(text)
    except Exception as e:
        logger.warning(f"JSON loads failed: {e}")
        return None
