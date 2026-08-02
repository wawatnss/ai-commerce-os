"""
Prompt Templates for Brand Builder

This module contains versioned, configurable prompt templates for brand generation.
All prompts are externalized and independent for easy replacement.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class PromptTemplate(BaseModel):
    """A prompt template with version and configuration."""
    name: str = Field(..., description="Template name")
    version: str = Field(..., description="Template version")
    template: str = Field(..., description="Prompt template with placeholders")
    placeholders: Dict[str, str] = Field(default_factory=dict, description="Placeholder descriptions")
    config: Dict[str, Any] = Field(default_factory=dict, description="Template configuration")


class PromptLibrary:
    """
    Library of prompt templates for brand generation.
    
    All prompts are versioned and configurable.
    """
    
    def __init__(self):
        self._templates: Dict[str, PromptTemplate] = {}
        self._initialize_templates()
    
    def _initialize_templates(self) -> None:
        """Initialize all prompt templates."""
        
        # Name Generation Template
        self._templates["name"] = PromptTemplate(
            name="name",
            version="1.0",
            template="""Generate 5-10 creative brand names for a {category} product with the following characteristics:
- Product: {product_name}
- Target audience: {target_audience}
- Unique value: {unique_value}
- Vibe: {vibe}

Requirements:
- Names should be memorable and easy to pronounce
- Names should be available as domain names (check availability)
- Names should reflect the product's unique value
- Names should appeal to the target audience
- Avoid trademark conflicts

Return as a JSON array of objects with:
- name
- meaning
- domain_availability (estimated)
- tagline""",
            placeholders={
                "category": "Product category",
                "product_name": "Name of the product",
                "target_audience": "Target customer segment",
                "unique_value": "Unique selling proposition",
                "vibe": "Brand personality/vibe"
            },
            config={"max_tokens": 500, "temperature": 0.8}
        )
        
        # Audience Persona Template
        self._templates["audience"] = PromptTemplate(
            name="audience",
            version="1.0",
            template="""Create a detailed customer persona for a {category} brand targeting {target_audience}.

Product: {product_name}
Brand values: {brand_values}

Generate a persona including:
- Demographics (age, gender, location, income)
- Psychographics (values, interests, lifestyle)
- Pain points and needs
- Buying behavior
- Communication preferences
- Media consumption habits

Return as JSON with all persona details.""",
            placeholders={
                "category": "Product category",
                "target_audience": "Target segment",
                "product_name": "Product name",
                "brand_values": "Core brand values"
            },
            config={"max_tokens": 800, "temperature": 0.7}
        )
        
        # Mission and Vision Template
        self._templates["mission_vision"] = PromptTemplate(
            name="mission_vision",
            version="1.0",
            template="""Generate mission and vision statements for a {category} brand.

Brand name: {brand_name}
Product: {product_name}
Target audience: {target_audience}
Unique value: {unique_value}

Requirements:
- Mission: What the brand does today (concise, actionable)
- Vision: What the brand aspires to become (inspiring, forward-looking)
- Both should be memorable and meaningful
- Align with target audience values

Return as JSON with mission and vision statements.""",
            placeholders={
                "category": "Product category",
                "brand_name": "Brand name",
                "product_name": "Product name",
                "target_audience": "Target segment",
                "unique_value": "Unique selling proposition"
            },
            config={"max_tokens": 400, "temperature": 0.7}
        )
        
        # Color Palette Template
        self._templates["colors"] = PromptTemplate(
            name="colors",
            version="1.0",
            template="""Generate a color palette for a {category} brand.

Brand name: {brand_name}
Product: {product_name}
Target audience: {target_audience}
Brand vibe: {vibe}

Requirements:
- Generate 3-5 colors (primary, secondary, accent)
- Provide hex codes
- Explain color psychology and rationale
- Ensure colors work well together
- Consider accessibility and contrast
- Colors should align with {vibe} vibe

Return as JSON with:
- color_name
- hex_code
- psychological_meaning
- usage_recommendation""",
            placeholders={
                "category": "Product category",
                "brand_name": "Brand name",
                "product_name": "Product name",
                "target_audience": "Target segment",
                "vibe": "Brand personality"
            },
            config={"max_tokens": 600, "temperature": 0.6}
        )
        
        # Typography Template
        self._templates["typography"] = PromptTemplate(
            name="typography",
            version="1.0",
            template="""Recommend typography for a {category} brand.

Brand name: {brand_name}
Product: {product_name}
Target audience: {target_audience}
Brand vibe: {vibe}

Requirements:
- Recommend 2-3 fonts (headline, body, accent)
- Consider readability across platforms
- Fonts should reflect {vibe} vibe
- Consider web availability (Google Fonts)
- Provide pairing rationale

Return as JSON with:
- font_name
- category (heading/body/accent)
- style
- usage_guidelines
- pairing_rationale""",
            placeholders={
                "category": "Product category",
                "brand_name": "Brand name",
                "product_name": "Product name",
                "target_audience": "Target segment",
                "vibe": "Brand personality"
            },
            config={"max_tokens": 500, "temperature": 0.5}
        )
        
        # Tone of Voice Template
        self._templates["tone"] = PromptTemplate(
            name="tone",
            version="1.0",
            template="""Define the tone of voice for a {category} brand.

Brand name: {brand_name}
Product: {product_name}
Target audience: {target_audience}
Brand values: {brand_values}

Requirements:
- Define primary tone (e.g., professional, friendly, playful)
- Define secondary tones
- Provide writing guidelines
- Include examples of do's and don'ts
- Consider platform-specific adaptations
- Should align with {target_audience} preferences

Return as JSON with:
- primary_tone
- secondary_tones
- writing_guidelines
- examples""",
            placeholders={
                "category": "Product category",
                "brand_name": "Brand name",
                "product_name": "Product name",
                "target_audience": "Target segment",
                "brand_values": "Core brand values"
            },
            config={"max_tokens": 700, "temperature": 0.6}
        )
        
        # Value Proposition Template
        self._templates["value_proposition"] = PromptTemplate(
            name="value_proposition",
            version="1.0",
            template="""Generate a unique value proposition for a {category} brand.

Brand name: {brand_name}
Product: {product_name}
Target audience: {target_audience}
Unique features: {unique_features}
Competitors: {competitors}

Requirements:
- Clear, concise, compelling
- Differentiates from competitors
- Addresses customer pain points
- Easy to understand and remember
- Should fit in a tagline

Return as JSON with:
- unique_value_proposition
- supporting_points
- elevator_pitch""",
            placeholders={
                "category": "Product category",
                "brand_name": "Brand name",
                "product_name": "Product name",
                "target_audience": "Target segment",
                "unique_features": "Unique product features",
                "competitors": "Key competitors"
            },
            config={"max_tokens": 500, "temperature": 0.7}
        )
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name."""
        return self._templates.get(name)
    
    def render_template(self, name: str, **kwargs) -> str:
        """
        Render a template with provided values.
        
        Args:
            name: Template name
            **kwargs: Values for placeholders
            
        Returns:
            Rendered prompt string
        """
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template '{name}' not found")
        
        # Simple string replacement
        rendered = template.template
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            if placeholder in rendered:
                rendered = rendered.replace(placeholder, str(value))
        
        return rendered
    
    def list_templates(self) -> list:
        """List all available template names."""
        return list(self._templates.keys())
    
    def get_template_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Get template configuration."""
        template = self.get_template(name)
        return template.config if template else None


# Global prompt library instance
prompt_library = PromptLibrary()
