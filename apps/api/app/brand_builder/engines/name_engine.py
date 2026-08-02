"""
Name Engine

Generates brand names based on product and audience data.
"""

from typing import Dict, Any, Optional
from .base import BaseBrandEngine, EngineResult
from ..prompts.templates import prompt_library


class NameEngine(BaseBrandEngine):
    """
    Engine for generating brand names.
    
    Generates creative, memorable brand names that align with the product and target audience.
    """
    
    async def generate(self, context: Dict[str, Any]) -> EngineResult:
        """
        Generate brand names.
        
        Args:
            context: Context data including product_name, category, target_audience, etc.
            
        Returns:
            EngineResult with generated brand names
        """
        try:
            # Get prompt template
            template = prompt_library.get_template("name")
            if not template:
                return EngineResult(
                    engine_name=self.engine_name,
                    success=False,
                    data={},
                    confidence=0,
                    metadata={"error": "Template not found"}
                )
            
            # Get template config
            config = prompt_library.get_template_config("name") or {}
            
            # Render template with context
            prompt = prompt_library.render_template(
                "name",
                category=context.get("category", "product"),
                product_name=context.get("product_name", "Product"),
                target_audience=context.get("target_audience", "general consumers"),
                unique_value=context.get("unique_value", "quality"),
                vibe=context.get("vibe", "modern")
            )
            
            # Generate using AI provider
            if self.ai_provider:
                result = await self.ai_provider.generate(
                    prompt=prompt,
                    temperature=config.get("temperature", 0.8),
                    max_tokens=config.get("max_tokens", 500)
                )
                
                # Parse result (in production, would parse JSON)
                # For now, return raw result
                return EngineResult(
                    engine_name=self.engine_name,
                    success=True,
                    data={"raw_result": result, "suggestions": self._parse_names(result)},
                    confidence=75,
                    metadata={"template_version": template.version}
                )
            else:
                # Fallback to mock generation
                return self._mock_generate(context)
                
        except Exception as e:
            return EngineResult(
                engine_name=self.engine_name,
                success=False,
                data={},
                confidence=0,
                metadata={"error": str(e)}
            )
    
    def _parse_names(self, result: str) -> list:
        """Parse AI result into name suggestions."""
        # In production, this would parse JSON from AI response
        # For now, return simple list
        return result.split("\n") if result else []
    
    def _mock_generate(self, context: Dict[str, Any]) -> EngineResult:
        """Mock generation for testing without AI."""
        product_name = context.get("product_name", "Product")
        category = context.get("category", "General")
        
        # Generate mock names based on product name
        suggestions = [
            f"{product_name.capitalize()}Pro",
            f"{category.capitalize()}Hub",
            f"{product_name.capitalize()}Direct",
            f"Pure{product_name.capitalize()}",
            f"{product_name.capitalize()}Co"
        ]
        
        return EngineResult(
            engine_name=self.engine_name,
            success=True,
            data={
                "suggestions": suggestions,
                "selected": suggestions[0]
            },
            confidence=60,
            metadata={"method": "mock"}
        )
