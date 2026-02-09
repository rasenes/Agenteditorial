from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

try:
    from dotenv import load_dotenv
except Exception:  # noqa: BLE001
    def load_dotenv() -> None:
        return None


load_dotenv()


@dataclass
class AppMetaConfig:
    app_name: str = "Editorial Agent IA"
    version: str = "2.0.0"
    debug: bool = False
    environment: str = "development"
    log_level: str = "INFO"


@dataclass
class APIConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    prefix: str = "/api/v1"
    cors_origins: list[str] = field(default_factory=lambda: ["*"])


@dataclass
class LLMRuntimeConfig:
    primary_provider: str = "ollama"
    fallback_order: list[str] = field(default_factory=lambda: ["ollama", "openai", "groq"])
    request_timeout_sec: float = 4.0
    max_retries: int = 1


@dataclass
class OllamaConfig:
    base_url: str = "http://localhost:11434"
    model: str = "llama3.1:8b"
    temperature: float = 0.7


@dataclass
class OpenAIConfig:
    api_key: str = ""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7


@dataclass
class GroqConfig:
    api_key: str = ""
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7


@dataclass
class SourcesConfig:
    rss_feeds: list[str] = field(
        default_factory=lambda: [
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
            "https://www.reddit.com/r/worldnews/.rss",
        ]
    )
    newsapi_key: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "editorial-agent/1.0"
    enable_twitter_trends: bool = False
    enable_youtube_trends: bool = False
    max_trends_per_source: int = 20


@dataclass
class MemoryConfig:
    path: str = "backend/data/memory.json"
    max_tweets: int = 2000
    max_history: int = 500


@dataclass
class CacheConfig:
    enabled: bool = True
    ttl_seconds: int = 300
    max_size: int = 1024


@dataclass
class GenerationConfig:
    default_theme: str = "IA"
    default_language: str = "fr"
    supported_languages: list[str] = field(default_factory=lambda: ["en", "fr", "es", "de"])
    candidates_per_request: int = 9
    max_parallel_generations: int = 4


@dataclass
class Settings:
    app: AppMetaConfig = field(default_factory=AppMetaConfig)
    api: APIConfig = field(default_factory=APIConfig)
    llm: LLMRuntimeConfig = field(default_factory=LLMRuntimeConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    groq: GroqConfig = field(default_factory=GroqConfig)
    sources: SourcesConfig = field(default_factory=SourcesConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)



def _merge_dataclass(instance: Any, data: dict[str, Any]) -> None:
    for key, value in data.items():
        if hasattr(instance, key):
            setattr(instance, key, value)



def _apply_env_overrides(settings: Settings) -> None:
    settings.openai.api_key = os.getenv("OPENAI_API_KEY", settings.openai.api_key)
    settings.groq.api_key = os.getenv("GROQ_API_KEY", settings.groq.api_key)
    settings.sources.newsapi_key = os.getenv("NEWSAPI_KEY", settings.sources.newsapi_key)
    settings.ollama.base_url = os.getenv("OLLAMA_BASE_URL", settings.ollama.base_url)
    settings.llm.primary_provider = os.getenv("LLM_PROVIDER", settings.llm.primary_provider)



def load_settings() -> Settings:
    root = Path(__file__).resolve().parents[2]
    config_file = root / "settings.yaml"
    settings = Settings()

    if config_file.exists():
        raw = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
        _merge_dataclass(settings.app, raw.get("app", {}))
        _merge_dataclass(settings.api, raw.get("api", {}))
        _merge_dataclass(settings.llm, raw.get("llm", {}))
        _merge_dataclass(settings.ollama, raw.get("ollama", {}))
        _merge_dataclass(settings.openai, raw.get("openai", {}))
        _merge_dataclass(settings.groq, raw.get("groq", {}))
        _merge_dataclass(settings.sources, raw.get("sources", {}))
        _merge_dataclass(settings.memory, raw.get("memory", {}))
        _merge_dataclass(settings.cache, raw.get("cache", {}))
        _merge_dataclass(settings.generation, raw.get("generation", {}))

    _apply_env_overrides(settings)
    return settings


SETTINGS = load_settings()
