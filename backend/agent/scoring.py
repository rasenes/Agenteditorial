"""
Système de scoring avancé pour les tweets.
Score basé sur : longueur, clarté, émotion, punchline, potentiel viral, etc.
"""

import re
from typing import Dict, List
from dataclasses import dataclass

from ..core.logger import get_logger
from ..core.utils import estimate_tweet_length
from ..models.tweet import Tweet

logger = get_logger(__name__)


@dataclass
class ScoreBreakdown:
    """Détail du score d'un tweet."""
    total: float
    length: float
    clarity: float
    emotion: float
    mirror: float
    punchline: float
    contradiction: float
    viral: float


class TweetScorer:
    """Score les tweets selon plusieurs critères."""
    
    def __init__(self):
        # Patterns pour détecter les éléments
        self.question_pattern = r"\?$"
        self.hashtag_pattern = r"#\w+"
        self.emoji_pattern = r"[😀-🙏🌀-🗿]"
        self.url_pattern = r"https?://\S+"
        self.caps_pattern = r"[A-Z]{3,}"  # 3+ lettres majuscules
        self.all_caps_pattern = r"^[A-Z\s\d\!\?]+$"  # Texte entièrement en majuscules
        
        # Emotional keywords
        self.strong_emotions = ["adorable", "magnifique", "horrible", "inacceptable", "dégoutant",
                               "excellent", "catastrophe", "crise", "révolution", "scandale"]
        self.weak_emotions = ["bien", "assez", "plutôt", "un peu", "à peine"]
    
    def score(self, tweet: Tweet) -> ScoreBreakdown:
        """
        Score un tweet sur multiple dimensions.
        
        Args:
            tweet: Tweet à scorer
        
        Returns:
            ScoreBreakdown avec tous les scores
        """
        text = tweet.content
        
        # Scores individuels (0-1)
        length_score = self._score_length(text)
        clarity_score = self._score_clarity(text)
        emotion_score = self._score_emotion(text)
        mirror_score = self._score_mirror(text)
        punchline_score = self._score_punchline(text)
        contradiction_score = self._score_contradiction(text)
        viral_score = self._score_viral(text)
        
        # Score total (moyenne pondérée)
        weights = {
            "length": 0.15,
            "clarity": 0.15,
            "emotion": 0.15,
            "mirror": 0.10,
            "punchline": 0.15,
            "contradiction": 0.15,
            "viral": 0.15,
        }
        
        total = (
            length_score * weights["length"] +
            clarity_score * weights["clarity"] +
            emotion_score * weights["emotion"] +
            mirror_score * weights["mirror"] +
            punchline_score * weights["punchline"] +
            contradiction_score * weights["contradiction"] +
            viral_score * weights["viral"]
        )
        
        breakdown = ScoreBreakdown(
            total=total,
            length=length_score,
            clarity=clarity_score,
            emotion=emotion_score,
            mirror=mirror_score,
            punchline=punchline_score,
            contradiction=contradiction_score,
            viral=viral_score,
        )
        
        # Update tweet
        tweet.score = total
        tweet.length_score = length_score
        tweet.clarity_score = clarity_score
        tweet.emotion_score = emotion_score
        tweet.mirror_score = mirror_score
        tweet.punchline_score = punchline_score
        tweet.contradiction_score = contradiction_score
        tweet.viral_score = viral_score
        
        return breakdown
    
    def _score_length(self, text: str) -> float:
        """Score la longueur optimale (150-260 chars)."""
        length = estimate_tweet_length(text)
        
        # Optimum : 150-260 chars
        if 150 <= length <= 260:
            return 1.0
        elif 100 <= length < 150:
            return 0.8  # Un peu court
        elif 260 < length <= 280:
            return 0.9  # Un peu long mais acceptable
        elif 50 <= length < 100:
            return 0.5  # Très court
        else:
            return 0.3  # Trop court ou trop long
    
    def _score_clarity(self, text: str) -> float:
        """Score la clarté du message."""
        score = 1.0
        
        # Penalize abbreviations excessives
        abbrev_count = len(re.findall(r"\b[a-z]{1,2}\b", text))
        if abbrev_count > 5:
            score -= 0.2
        
        # Penalize excessive punctuation
        punct_ratio = len(re.findall(r"[!?\.]{2,}", text)) / (len(text) / 100 + 1)
        if punct_ratio > 0.1:
            score -= 0.1
        
        # Bonus pour structure claire
        sentences = len(re.split(r"[.!?;]", text.strip()))
        if sentences <= 3:
            score += 0.1
        
        # Bonus pour mots clés
        keywords = ["important", "évidement", "précis", "clair", "vrai"]
        if any(kw in text.lower() for kw in keywords):
            score += 0.05
        
        return max(0, min(score, 1.0))
    
    def _score_emotion(self, text: str) -> float:
        """Score la charge émotionnelle."""
        text_lower = text.lower()
        score = 0.5  # Neutre par défaut
        
        # Compte les émotions fortes
        strong_count = sum(1 for e in self.strong_emotions if e in text_lower)
        score += strong_count * 0.15
        
        # Compte les émotions faibles
        weak_count = sum(1 for e in self.weak_emotions if e in text_lower)
        score -= weak_count * 0.05
        
        # Bonus pour emojis
        if re.search(self.emoji_pattern, text):
            score += 0.1
        
        # Bonus pour majuscules (emphase)
        caps_words = len(re.findall(self.caps_pattern, text))
        if caps_words > 0:
            score += min(caps_words * 0.05, 0.15)
        
        # Penalize tout majuscules (sauf short)
        if len(text) > 20 and re.match(self.all_caps_pattern, text):
            score -= 0.3
        
        return max(0, min(score, 1.0))
    
    def _score_mirror(self, text: str) -> float:
        """Score l'effet miroir (parler du lecteur)."""
        text_lower = text.lower()
        mirror_words = ["vous", "tu", "votre", "ton", "toi", "nous", "on", "ta", "tes", "vos"]
        
        count = sum(text_lower.count(w) for w in mirror_words)
        
        # 1-2 occurrences = bon
        if count == 0:
            return 0.3
        elif 1 <= count <= 2:
            return 0.8
        elif count <= 4:
            return 0.9
        else:
            return 0.6  # Trop d'occurrences = pas naturel
    
    def _score_punchline(self, text: str) -> float:
        """Score la présence d'une punchline (humor, twist, conclusion)."""
        score = 0.3
        
        # Patterns de punchline
        patterns = [
            r"\.?\?[^.]*$",  # Fin avec question
            r"mais\s+[^.]+\.$",  # "mais" suivi de conclusion
            r"d'ailleurs",  # Transition vers detail
            r"au fait",  # Revelation
            r"spoiler",  # Avant une révélation
            r"attends",  # Invitation à attendre la suite
        ]
        
        for pattern in patterns:
            if re.search(pattern, text.lower()):
                score += 0.15
        
        # Bonus pour ironie détectée
        if "soit-disant" in text.lower() or "prétendument" in text.lower():
            score += 0.15
        
        # Bonus pour contraste
        if " mais " in text.lower() or " au contraire" in text.lower():
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_contradiction(self, text: str) -> float:
        """Score la présence de contradictions intéressantes."""
        score = 0.2
        
        patterns = [
            r"mais|cependant|pourtant|alors que|au contraire|sauf que|ne pas",
        ]
        
        for pattern in patterns:
            if re.search(pattern, text.lower()):
                score += 0.2
        
        return min(score, 1.0)
    
    def _score_viral(self, text: str) -> float:
        """Score le potentiel viral global."""
        score = 0.4
        
        # Viral keywords
        viral_keywords = [
            "trending", "buzz", "breaking", "alert", "importante",
            "révèle", "changemment", "nouveau", "choquant",
            "record", "jamais", "première", "découverte",
        ]
        
        text_lower = text.lower()
        for kw in viral_keywords:
            if kw in text_lower:
                score += 0.1
        
        # Hashtags (bon pour viral)
        hashtags = len(re.findall(self.hashtag_pattern, text))
        score += min(hashtags * 0.1, 0.2)
        
        # URLs (bon pour viral)
        urls = len(re.findall(self.url_pattern, text))
        score += min(urls * 0.1, 0.15)
        
        # Emojis (bon pour engagement)
        emojis = len(re.findall(self.emoji_pattern, text))
        score += min(emojis * 0.05, 0.1)
        
        # Mention d'une tendance (trend connection)
        if any(trend_word in text.lower() for trend_word in ["IA", "tech", "crypto", "startup"]):
            score += 0.1
        
        return min(score, 1.0)
    
    def sort_tweets(self, tweets: List[Tweet], reverse: bool = True) -> List[Tweet]:
        """
        Score et trie les tweets.
        
        Args:
            tweets: Liste de tweets
            reverse: Si True, meilleurs d'abord
        
        Returns:
            Tweets triés par score
        """
        for tweet in tweets:
            self.score(tweet)
        
        return sorted(tweets, key=lambda t: t.score, reverse=reverse)
    
    def get_top(self, tweets: List[Tweet], n: int = 3) -> List[Tweet]:
        """Retourne les N meilleurs tweets."""
        return self.sort_tweets(tweets)[:n]


# Instance globale
scorer = TweetScorer()
