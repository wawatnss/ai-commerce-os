"""
Visual Engine

Generates visual identity elements (colors, typography, logo prompts).
"""

from typing import Dict, Any, Optional
from .base import BaseBrandEngine, EngineResult
from ..prompts.templates import prompt_library


class VisualEngine(BaseBrandEngine):
    """Engine for generating visual identity (colors, typography, logo prompts)."""
    
    async def generate(self, context: Dict[str, Any]) -> EngineResult:
        """Generate visual identity."""
        try:
            # Generate colors
            colors_result = await self._generate_colors(context)
            
            # Generate typography
            typography_result = await self._generate_typography(context)
            
            # Generate logo prompt
            logo_prompt = self._generate_logo_prompt(context)
            
            return EngineResult(
                engine_name=self.engine_name,
                success=True,
                data={
                    "color_palette": colors_result.data.get("palette", {}),
                    "typography": typography_result.data.get("typography", {}),
                    "logo_prompt": logo_prompt,
                    "packaging_prompt": self._generate_packaging_prompt(context),
                    "product_photography_prompt": self._generate_photography_prompt(context),
                    "hero_banner_prompt": self._generate_banner_prompt(context)
                },
                confidence=70,
                metadata={"components": ["colors", "typography", "prompts"]}
            )
                
        except Exception as e:
            return EngineResult(
                engine_name=self.engine_name,
                success=False,
                data={},
                confidence=0,
                metadata={"error": str(e)}
            )
    
    async def _generate_colors(self, context: Dict[str, Any]) -> EngineResult:
        """Generate color palette."""
        template = prompt_library.get_template("colors")
        if not template:
            return EngineResult(engine_name="colors", success=False, data={}, confidence=0)
        
        config = prompt_library.get_template_config("colors") or {}
        
        prompt = prompt_library.render_template(
            "colors",
            category=context.get("category", "product"),
            brand_name=context.get("brand_name", "Brand"),
            product_name=context.get("product_name", "Product"),
            target_audience=context.get("target_audience", "general"),
            vibe=context.get("vibe", "modern")
        )
        
        if self.ai_provider:
            result = await self.ai_provider.generate(
                prompt=prompt,
                temperature=config.get("temperature", 0.6),
                max_tokens=config.get("max_tokens", 600)
            )
            return EngineResult(
                engine_name="colors",
                success=True,
                data={"palette": self._parse_colors(result)},
                confidence=75
            )
        else:
            return self._mock_colors(context)
    
    async def _generate_typography(self, context: Dict[str, Any]) -> EngineResult:
        """Generate typography recommendations."""
        template = prompt_library.get_template("typography")
        if not template:
            return EngineResult(engine_name="typography", success=False, data={}, confidence=0)
        
        config = prompt_library.get_template_config("typography") or {}
        
        prompt = prompt_library.render_template(
            "typography",
            category=context.get("category", "product"),
            brand_name=context.get("brand_name", "Brand"),
            product_name=context.get("product_name", "Product"),
            target_audience=context.get("target_audience", "general"),
            vibe=context.get("vibe", "modern")
        )
        
        if self.ai_provider:
            result = await self.ai_provider.generate(
                prompt=prompt,
                temperature=config.get("temperature", 0.5),
                max_tokens=config.get("max_tokens", 500)
            )
            return EngineResult(
                engine_name="typography",
                success=True,
                data={"typography": self._parse_typography(result)},
                confidence=75
            )
        else:
            return self._mock_typography(context)
    
    def _generate_logo_prompt(self, context: Dict[str, Any]) -> str:
        """Generate logo design prompt."""
        brand_name = context.get("brand_name", "Brand")
        vibe = context.get("vibe", "modern")
        return f"Create a modern, minimalist logo for {brand_name} with a {vibe} aesthetic. Clean lines, memorable, suitable for e-commerce."
    
    def _generate_packaging_prompt(self, context: Dict[str, Any]) -> str:
        """Generate packaging design prompt."""
        brand_name = context.get("brand_name", "Brand")
        return f"Design packaging for {brand_name} that reflects quality and sustainability. Minimalist design with clear branding."
    
    def _generate_photography_prompt(self, context: Dict[str, Any]) -> str:
        """Generate product photography prompt."""
        brand_name = context.get("brand_name", "Brand")
        vibe = context.get("vibe", "modern")
        return f"Professional product photography for {brand_name} with {vibe} aesthetic. Clean backgrounds, high contrast, lifestyle shots."
    
    def _generate_banner_prompt(self, context: Dict[str, Any]) -> str:
        """Generate hero banner prompt."""
        brand_name = context.get("brand_name", "Brand")
        return f"Create a hero banner for {brand_name} showcasing the product with lifestyle context. Modern, clean, conversion-focused."
    
    def _parse_colors(self, result: str) -> Dict[str, Any]:
        """Parse colors result."""
        return {"raw": result}
    
    def _parse_typography(self, result: str) -> Dict[str, Any]:
        """Parse typography result."""
        return {"raw": result}
    
    def _mock_colors(self, context: Dict[str, Any]) -> EngineResult:
        """Mock colors generation."""
        return EngineResult(
            engine_name="colors",
            success=True,
            data={
                "palette": {
                    "primary": {"hex": "#2563EB", "name": "Royal Blue", "meaning": "Trust, professionalism"},
                    "secondary": {"hex": "#10B981", "name": "Emerald", "meaning": "Growth, quality"},
                    "accent": {"hex": "#F59E0B", "name": "Amber", "meaning": "Energy, innovation"}
                }
            },
            confidence=60
        )
    
    def _mock_typography(self, context: Dict[str, Any]) -> EngineResult:
        """Mock typography generation."""
        return EngineResult(
            engine_name="typography",
            success=True,
            data={
                "typography": {
                    "heading": {"font": "Inter", "weight": "700"},
                    "body": {"font": "Inter", "weight": "400"},
                    "accent": {"font": "Space Grotesk", "weight": "600"}
                }
            },
            confidence=60
        )
