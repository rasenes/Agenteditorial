"""
Configuration centralisée pour l'application Editorial Agent.
Charge depuis settings.yaml et variables d'environnement.
"""

import os
import yaml
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    """Configuration LLM provider."""
    provider: str = "ollama"  # ollama, openai, groq
    model: str = "mistral"
    temperature: float = 0.7
    max_tokens: int = 500
    timeout: int = 30


@dataclass
class OllamaConfig:
    """Configuration Ollama."""
    base_url: str = "http://localhost:11434"
    model: str = "mistral"
    temperature: float = 0.7
    timeout: int = 30


@dataclass
class OpenAIConfig:
    """Configuration OpenAI."""
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    timeout: int = 30


@dataclass
class GroqConfig:
    """Configuration Groq."""
    api_key: str = ""
    model: str = "mixtral-8x7b-32768"
    temperature: float = 0.7
    timeout: int = 30


@dataclass
class SourcesConfig:
    """Configuration des sources de tendances."""
    rss_feeds: list = field(default_factory=list)
    newsapi_key: str = ""
    reddit_enabled: bool = False
    twitter_enabled: bool = False
    youtube_enabled: bool = False
    update_interval: int = 3600  # secondes


@dataclass
class MemoryConfig:
    """Configuration mémoire."""
    enabled: bool = True
    path: str = "backend/data/memory.json"
    max_size: int = 10000
    cleanup_interval: int = 86400  # 24h


@dataclass
class CacheConfig:
    """Configuration cache."""
    enabled: bool = True
    ttl: int = 3600  # secondes
    max_size: int = 1000


@dataclass
class AppConfig:
    """Configuration globale application."""
    app_name: str = "Editorial Agent IA"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    llm: LLMConfig = field(default_factory=LLMConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    groq: GroqConfig = field(default_factory=GroqConfig)
    sources: SourcesConfig = field(default_factory=SourcesConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"


def load_config() -> AppConfig:
    """Charge la configuration depuis settings.yaml et env vars."""
    config_path = Path(__file__).parent.parent.parent / "settings.yaml"
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}
    
    # Override avec env vars
    if os.getenv("OLLAMA_BASE_URL"):
        data.setdefault("ollama", {})["base_url"] = os.getenv("OLLAMA_BASE_URL")
    
    if os.getenv("OPENAI_API_KEY"):
        data.setdefault("openai", {})["api_key"] = os.getenv("OPENAI_API_KEY")
    
    if os.getenv("GROQ_API_KEY"):
        data.setdefault("groq", {})["api_key"] = os.getenv("GROQ_API_KEY")
    
    if os.getenv("LLM_PROVIDER"):
        data.setdefault("llm", {})["provider"] = os.getenv("LLM_PROVIDER")
    
    # Merge avec config defaults
    config = AppConfig()
    
    # Update LLM config
    if "llm" in data:
        for key, val in data["llm"].items():
            if hasattr(config.llm, key):
                setattr(config.llm, key, val)
    
    # Update Ollama config
    if "ollama" in data:
        for key, val in data["ollama"].items():
            if hasattr(config.ollama, key):
                setattr(config.ollama, key, val)
    
    # Update OpenAI config
    if "openai" in data:
        for key, val in data["openai"].items():
            if hasattr(config.openai, key):
                setattr(config.openai, key, val)
    
    # Update Groq config
    if "groq" in data:
        for key, val in data["groq"].items():
            if hasattr(config.groq, key):
                setattr(config.groq, key, val)
    
    # Update Sources config
    if "sources" in data:
        for key, val in data["sources"].items():
            if hasattr(config.sources, key):
                setattr(config.sources, key, val)
    
    # Update Memory config
    if "memory" in data:
        for key, val in data["memory"].items():
            if hasattr(config.memory, key):
                setattr(config.memory, key, val)
    
    # Update Cache config
    if "cache" in data:
        for key, val in data["cache"].items():
            if hasattr(config.cache, key):
                setattr(config.cache, key, val)
    
    # Update App config
    if "app" in data:
        for key, val in data["app"].items():
            if hasattr(config, key):
                setattr(config, key, val)
    
    return config


# Instance globale
CONFIG = load_config()
