"""
Messaging Engine

Generates tone of voice, writing style, and communication guidelines.
"""

from typing import Dict, Any, Optional
from .base import BaseBrandEngine, EngineResult
from ..prompts.templates import prompt_library


class MessagingEngine(BaseBrandEngine):
    """Engine for generating messaging and communication style."""
    
    async def generate(self, context: Dict[str, Any]) -> EngineResult:
        """Generate messaging guidelines."""
        try:
            # Generate tone of voice
            tone_result = await self._generate_tone(context)
            
            return EngineResult(
                engine_name=self.engine_name,
                success=True,
                data={
                    "tone_of_voice": tone_result.data.get("tone", {}),
                    "writing_style": tone_result.data.get("style", {}),
                    "social_media_style": self._generate_social_style(context),
                    "seo_style": self._generate_seo_style(context),
                    "email_style": self._generate_email_style(context)
                },
                confidence=70,
                metadata={"components": ["tone", "style", "guidelines"]}
            )
                
        except Exception as e:
            return EngineResult(
                engine_name=self.engine_name,
                success=False,
                data={},
                confidence=0,
                metadata={"error": str(e)}
            )
    
    async def _generate_tone(self, context: Dict[str, Any]) -> EngineResult:
        """Generate tone of voice."""
        template = prompt_library.get_template("tone")
        if not template:
            return EngineResult(engine_name="tone", success=False, data={}, confidence=0)
        
        config = prompt_library.get_template_config("tone") or {}
        
        prompt = prompt_library.render_template(
            "tone",
            category=context.get("category", "product"),
            brand_name=context.get("brand_name", "Brand"),
            product_name=context.get("product_name", "Product"),
            target_audience=context.get("target_audience", "general"),
            brand_values=context.get("brand_values", "quality, innovation")
        )
        
        if self.ai_provider:
            result = await self.ai_provider.generate(
                prompt=prompt,
                temperature=config.get("temperature", 0.6),
                max_tokens=config.get("max_tokens", 700)
            )
            return EngineResult(
                engine_name="tone",
                success=True,
                data={"tone": self._parse_tone(result), "style": self._parse_style(result)},
                confidence=75
            )
        else:
            return self._mock_tone(context)
    
    def _generate_social_style(self, context: Dict[str, Any]) -> str:
        """Generate social media style guidelines."""
        return "Engaging, visual, hashtag-driven, interactive, authentic voice."
    
    def _generate_seo_style(self, context: Dict[str, Any]) -> str:
        """Generate SEO writing style guidelines."""
        return "Keyword-rich, descriptive, benefit-focused, clear calls-to-action."
    
    def _generate_email_style(self, context: Dict[str, Any]) -> str:
        """Generate email writing style guidelines."""
        return "Personal, persuasive, value-focused, mobile-optimized, action-oriented."
    
    def _parse_tone(self, result: str) -> Dict[str, Any]:
        """Parse tone result."""
        return {"raw": result}
    
    def _parse_style(self, result: str) -> Dict[str, Any]:
        """Parse style result."""
        return {"raw": result}
    
    def _mock_tone(self, context: Dict[str, Any]) -> EngineResult:
        """Mock tone generation."""
        return EngineResult(
            engine_name="tone",
            success=True,
            data={
                "tone": {
                    "primary": "professional yet approachable",
                    "secondary": ["friendly", "informative", "encouraging"],
                    "guidelines": "Be clear, concise, and helpful. Avoid jargon."
                },
                "style": {
                    "voice": "authoritative but warm",
                    "do": ["use active voice", "be specific", "add value"],
                    "dont": ["be overly promotional", "use jargon", "be vague"]
                }
            },
            confidence=60
        )
