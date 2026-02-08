"""
Générateur de tweets IA.
Crée des tweets à partir de tendances avec différents styles.
"""

import asyncio
from typing import List, Optional
import json

from ..core.logger import get_logger
from ..core.utils import extract_json, truncate_text, validate_tweet, clean_text
from ..models.tweet import Tweet, Trend, GenerationRequest, GenerationResponse
from ..providers.router import router

logger = get_logger(__name__)


class TweetGenerator:
    """Génère des tweets à partir de tendances."""
    
    # Templates par style
    STYLE_TEMPLATES = {
        "normal": """Generate {count} professional and engaging tweets about: {topic}
        
Requirements:
- Clear and informative
- Optimized for X/Twitter (280 chars max)
- Include relevant hashtags
- Natural French
- Varied angles

Format as JSON array with 'content' field for each tweet.""",
        
        "aggressive": """Generate {count} provocative and bold tweets about: {topic}
        
Requirements:
- Direct and assertive
- Challenge assumptions
- Create debate
- Stay respectful but daring
- Natural French

Format as JSON array with 'content' field.""",
        
        "funny": """Generate {count} humorous and witty tweets about: {topic}
        
Requirements:
- Clever wordplay or observations
- Light and entertaining
- Relatable humor
- Natural French

Format as JSON array with 'content' field.""",
        
        "minimal": """Generate {count} ultra-short tweets about: {topic}
        
Requirements:
- Less than 150 characters
- Punchy and memorable
- Direct impact
- Minimal words
- Natural French

Format as JSON array with 'content' field.""",
        
        "data": """Generate {count} fact-based tweets about: {topic}
        
Requirements:
- Include numbers or statistics
- Backed by data
- Informative
- Professional tone
- Natural French

Format as JSON array with 'content' field.""",
    }
    
    THEME_PROMPTS = {
        "IA": "You are a tech influencer discussing AI breakthroughs",
        "Tech": "You are a tech industry expert discussing innovations",
        "Science": "You are a science communicator explaining discoveries",
        "Sport": "You are a sports commentator discussing sports news",
        "Politique": "You are a political analyst discussing current events",
        "Business": "You are a business strategist discussing entrepreneurship",
        "Crypto": "You are a crypto analyst discussing blockchain",
        "Univers": "You are a space enthusiast discussing astronomy",
        "Culture": "You are a cultural critic discussing arts and entertainment",
        "Humour": "You are a comedian and humorist",
        "Fait": "You are sharing surprising and interesting facts",
        "Philosophie": "You are a philosopher discussing ideas and existence",
        "Futur": "You are a futurist discussing tomorrow's world",
        "general": "You are a social media expert creating engaging content",
    }
    
    def __init__(self):
        self.router = router
    
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """
        Génère des tweets pour une requête.
        
        Args:
            request: Requête de génération
        
        Returns:
            Réponse avec tweets générés
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Prépare le contexte
            topic = ""
            if request.trend:
                topic = f"{request.trend.title}\n{request.trend.description}"
            
            if not topic:
                topic = f"Topic: {request.theme}"
            
            # Build prompt
            theme_context = self.THEME_PROMPTS.get(request.theme, self.THEME_PROMPTS["general"])
            style_template = self.STYLE_TEMPLATES.get(request.style, self.STYLE_TEMPLATES["normal"])
            
            prompt = f"""{theme_context}

Generate engaging tweets in French about:
{topic}

{style_template.format(count=request.count, topic=topic)}

Respond ONLY with valid JSON array, no other text."""
            
            # Génère avec LLM
            logger.info(f"Generating {request.count} tweets (style: {request.style}, theme: {request.theme})")
            response_text = await self.router.generate(
                prompt,
                temperature=0.7,
                max_tokens=800,
            )
            
            # Parse JSON
            json_data = self._parse_response(response_text)
            
            if not json_data:
                logger.error(f"Failed to parse LLM response: {response_text[:100]}")
                # Fallback simple
                tweets = [
                    Tweet(
                        content=truncate_text(topic, 250),
                        theme=request.theme,
                        language=request.language,
                    )
                ]
            else:
                tweets = []
                for item in json_data:
                    if isinstance(item, dict):
                        content = item.get("content", "") or item.get("text", "")
                    else:
                        content = str(item)
                    
                    if content:
                        content = clean_text(content)
                        is_valid, msg = validate_tweet(content)
                        
                        if is_valid:
                            tweet = Tweet(
                                content=content,
                                theme=request.theme,
                                language=request.language,
                                source="generated",
                            )
                            tweets.append(tweet)
                
                # Ensure minimum tweets
                while len(tweets) < request.count:
                    tweets.append(Tweet(
                        content=truncate_text(topic, 250),
                        theme=request.theme,
                        language=request.language,
                    ))
                
                tweets = tweets[:request.count]
            
            elapsed = asyncio.get_event_loop().time() - start_time
            
            return GenerationResponse(
                tweets=tweets,
                trend=request.trend,
                total_time=elapsed,
                model="llm-default",
            )
        
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            elapsed = asyncio.get_event_loop().time() - start_time
            
            return GenerationResponse(
                tweets=[],
                trend=request.trend,
                total_time=elapsed,
                model="error",
                metadata={"error": str(e)},
            )
    
    def _parse_response(self, response: str) -> Optional[List]:
        """Parse la réponse JSON du LLM."""
        try:
            # Essaie JSON direct
            return json.loads(response)
        except:
            pass
        
        # Essaie extract_json
        data = extract_json(response)
        if data:
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "tweets" in data:
                return data["tweets"]
        
        return None
    
    async def generate_batch(
        self,
        trends: List[Trend],
        theme: str = "general",
        style: str = "normal",
        count_per_trend: int = 2,
    ) -> List[GenerationResponse]:
        """
        Génère des tweets pour plusieurs tendances.
        
        Args:
            trends: Listes de tendances
            theme: Thème
            style: Style de génération
            count_per_trend: Nombre de tweets par tendance
        
        Returns:
            Listes de réponses
        """
        requests = [
            GenerationRequest(
                trend=trend,
                theme=trend.category if hasattr(trend, 'category') else theme,
                count=count_per_trend,
                style=style,
            )
            for trend in trends
        ]
        
        tasks = [self.generate(req) for req in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)


# Instance globale
generator = TweetGenerator()
