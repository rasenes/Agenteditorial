"""
Analyseur de tendances et sélecteur d'angle.
Détecte les angles viraux et génère des insights.
"""

import re
from typing import List, Dict, Tuple, Optional
from collections import Counter

from ..core.logger import get_logger
from ..models.tweet import Trend

logger = get_logger(__name__)


class TrendAnalyzer:
    """Analyse les tendances et détecte les angles viraux."""
    
    # Patterns pour détecter les angles viraux
    VIRAL_PATTERNS = {
        "contradiction": r"mais|cependant|pourtant|alors que|au contraire|sauf que",
        "surprise": r"révèle|étonnant|incroyable|jamais vu|inédit|BREAKING",
        "urgence": r"urgent|catastrophe|alerte|danger|critique|maintenant",
        "curiosité": r"pourquoi|comment|qu'est-ce|mystère|secret|révélation",
        "émotion": r"adorable|magnifique|horrible|inacceptable|dégoutant",
        "statistique": r"\d+%|chiffre|étude|rapport|données|analyse",
        "humour": r"mdr|lol|rigolo|blague|punchline|absurde",
        "ironie": r"bien sûr|évidemment|sans blague|prétendument|soit-disant",
    }
    
    VIRAL_KEYWORDS = [
        "IA", "tech", "crypto", "innovation", "révolution",
        "record", "découverte", "scandale", "clash",
        "trending", "viral", "buzz", "hype",
    ]
    
    def __init__(self):
        self.trends_cache: List[Trend] = []
    
    def analyze_viral_potential(self, text: str) -> Dict[str, float]:
        """
        Analyse le potentiel viral d'un texte.
        
        Args:
            text: Texte à analyser
        
        Returns:
            Dict avec scores pour chaque pattern
        """
        text_lower = text.lower()
        scores = {}
        
        for pattern_name, pattern in self.VIRAL_PATTERNS.items():
            matches = len(re.findall(pattern, text_lower))
            scores[pattern_name] = min(matches * 0.2, 1.0)
        
        # Bonus pour keywords viraux
        keyword_count = sum(
            text_lower.count(kw.lower())
            for kw in self.VIRAL_KEYWORDS
        )
        scores["keywords"] = min(keyword_count * 0.15, 1.0)
        
        return scores
    
    def extract_angles(self, trend: Trend) -> List[Dict[str, any]]:
        """
        Extrait les angles possibles d'une tendance.
        
        Args:
            trend: Tendance à analyser
        
        Returns:
            Liste d'angles avec scores
        """
        text = f"{trend.title} {trend.description}".lower()
        angles = []
        
        # Angle 1: Surprise/Révélation
        viral_scores = self.analyze_viral_potential(text)
        if viral_scores.get("surprise", 0) > 0.3:
            angles.append({
                "type": "surprise",
                "description": "Révéler un aspect inattendu",
                "score": viral_scores["surprise"],
                "prompt_suffix": "Rendre surprenant et dramatique",
            })
        
        # Angle 2: Contradiction/Débat
        if viral_scores.get("contradiction", 0) > 0.3:
            angles.append({
                "type": "contradiction",
                "description": "Créer une tension ou débat",
                "score": viral_scores["contradiction"],
                "prompt_suffix": "Créer une contradiction intéressante",
            })
        
        # Angle 3: Curiosité
        if viral_scores.get("curiosité", 0) > 0.3:
            angles.append({
                "type": "curiosity",
                "description": "Éveiller la curiosité",
                "score": viral_scores.get("curiosité", 0),
                "prompt_suffix": "Poser une question intrigante",
            })
        
        # Angle 4: Humour/Ironie
        if viral_scores.get("humour", 0) > 0.2 or viral_scores.get("ironie", 0) > 0.2:
            angles.append({
                "type": "humor",
                "description": "Utiliser l'humour ou l'ironie",
                "score": max(viral_scores.get("humour", 0), viral_scores.get("ironie", 0)),
                "prompt_suffix": "Ajouter de l'humour ou de l'ironie",
            })
        
        # Angle 5: Urgence
        if viral_scores.get("urgence", 0) > 0.3:
            angles.append({
                "type": "urgency",
                "description": "Créer un sentiment d'urgence",
                "score": viral_scores["urgence"],
                "prompt_suffix": "Créer un sentiment d'imminence",
            })
        
        # Angle 6: Statistique/Fait
        if viral_scores.get("statistique", 0) > 0.3:
            angles.append({
                "type": "stat",
                "description": "Mettre en avant un chiffre ou un fait",
                "score": viral_scores["statistique"],
                "prompt_suffix": "Mettre en avant un chiffre ou une statistique",
            })
        
        # Si pas d'angles trouvés, utiliser des angles génériques
        if not angles:
            angles = [
                {
                    "type": "standard",
                    "description": "Format standard et direct",
                    "score": 0.7,
                    "prompt_suffix": "Être direct et informatif",
                },
                {
                    "type": "emotional",
                    "description": "Approche émotionnelle",
                    "score": 0.6,
                    "prompt_suffix": "Ajouter une touche émotionnelle",
                },
            ]
        
        # Trie par score
        angles.sort(key=lambda x: x["score"], reverse=True)
        return angles
    
    def categorize_trend(self, text: str) -> str:
        """
        Catégorise une tendance.
        
        Args:
            text: Texte à catégoriser
        
        Returns:
            Catégorie (IA, Tech, Science, etc.)
        """
        text_lower = text.lower()
        
        categories = {
            "IA": ["ia", "ai", "intelligence artificielle", "llm", "neural"],
            "Tech": ["tech", "startup", "code", "software", "app", "digital"],
            "Science": ["science", "recherche", "découverte", "étude", "physique"],
            "Sport": ["sport", "foot", "foot", "tennis", "match", "athlète"],
            "Politique": ["politique", "gouvernement", "élection", "président"],
            "Business": ["business", "finance", "startup", "entrepreneur"],
            "Crypto": ["crypto", "bitcoin", "ethereum", "blockchain", "nft"],
            "Univers": ["espace", "nasa", "planète", "galaxie", "univers"],
            "Culture": ["culture", "cinéma", "musique", "art", "livre"],
            "Humour": ["blague", "mdr", "lol", "funny", "comedian"],
            "Fait": ["fait", "insolite", "anormal", "bizarre", "étrange"],
            "Philosophie": ["philosophie", "pensée", "existence", "senss"],
            "Futur": ["futur", "demain", "prédiction", "tendance", "évolution"],
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        
        return "général"
    
    def score_trends(self, trends: List[Trend]) -> List[Trend]:
        """
        Score les tendances selon leur potentiel viral.
        
        Args:
            trends: Listes de tendances
        
        Returns:
            Tendances scored et triées
        """
        for trend in trends:
            text = f"{trend.title} {trend.description}"
            
            # Analyse virale
            viral_scores = self.analyze_viral_potential(text)
            avg_viral = sum(viral_scores.values()) / len(viral_scores) if viral_scores else 0
            
            # Catégorie
            trend.category = self.categorize_trend(text)
            
            # Score final (combinaison)
            trend.trending_score = (trend.trending_score * 0.5) + (avg_viral * 0.5)
        
        # Trie par score
        return sorted(trends, key=lambda t: t.trending_score, reverse=True)


# Instance globale
analyzer = TrendAnalyzer()
