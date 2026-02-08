"""
Modèles de données pour tweets et tendances.
Utilisés dans l'API et l'agent.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


@dataclass
class Tweet:
    """Modèle de tweet avec metadata."""
    content: str
    score: float = 0.0
    theme: str = "general"
    source: str = "generated"
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    id: Optional[str] = None
    
    # Scores détaillés
    length_score: float = 0.0
    clarity_score: float = 0.0
    emotion_score: float = 0.0
    mirror_score: float = 0.0
    punchline_score: float = 0.0
    contradiction_score: float = 0.0
    viral_score: float = 0.0
    
    # Metadata
    language: str = "fr"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convertit en JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)
    
    @staticmethod
    def from_dict(data: dict) -> "Tweet":
        """Crée depuis un dictionnaire."""
        return Tweet(**{k: v for k, v in data.items() if k in Tweet.__dataclass_fields__})
    
    def __str__(self) -> str:
        return f"[{self.theme}] ({self.score:.2f}) {self.content[:80]}"


@dataclass
class Trend:
    """Modèle de tendance avec détails."""
    title: str
    description: str = ""
    category: str = "general"
    source: str = "unknown"
    trending_score: float = 0.0
    url: str = ""
    language: str = "en"
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    id: Optional[str] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    related_keywords: List[str] = field(default_factory=list)
    engagement: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Génération associée
    generated_tweets: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convertit en JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)
    
    @staticmethod
    def from_dict(data: dict) -> "Trend":
        """Crée depuis un dictionnaire."""
        return Trend(**{k: v for k, v in data.items() if k in Trend.__dataclass_fields__})
    
    def __str__(self) -> str:
        return f"[{self.source}] {self.title}"


@dataclass
class GenerationRequest:
    """Requête de génération de tweets."""
    trend: Optional[Trend] = None
    theme: str = "general"
    count: int = 3
    style: str = "normal"  # normal, aggressive, funny, minimal
    language: str = "fr"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GenerationResponse:
    """Réponse de génération."""
    tweets: List[Tweet]
    trend: Optional[Trend] = None
    total_time: float = 0.0
    model: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "tweets": [t.to_dict() for t in self.tweets],
            "trend": self.trend.to_dict() if self.trend else None,
            "total_time": self.total_time,
            "model": self.model,
            "metadata": self.metadata,
        }
