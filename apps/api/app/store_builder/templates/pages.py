"""
Store Page Templates

This module contains versioned templates for different store pages.
All templates are externalized and easily replaceable.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class PageTemplate(BaseModel):
    """A page template with version and configuration."""
    name: str = Field(..., description="Template name")
    version: str = Field(..., description="Template version")
    template: str = Field(..., description="Template content with placeholders")
    placeholders: Dict[str, str] = Field(default_factory=dict, description="Placeholder descriptions")
    config: Dict[str, Any] = Field(default_factory=dict, description="Template configuration")


class TemplateLibrary:
    """Library of store page templates."""
    
    def __init__(self):
        self._templates: Dict[str, PageTemplate] = {}
        self._initialize_templates()
    
    def _initialize_templates(self) -> None:
        """Initialize all page templates."""
        
        # Homepage Template
        self._templates["homepage"] = PageTemplate(
            name="homepage",
            version="1.0",
            template="""Homepage for {store_name}

Hero Section:
- Headline: {hero_headline}
- Subheadline: {hero_subheadline}
- CTA: {hero_cta}
- Background: {hero_background}

Features Section:
- Feature 1: {feature_1}
- Feature 2: {feature_2}
- Feature 3: {feature_3}

Testimonials Section:
- Customer testimonial: {testimonial}
- Rating: {rating}

Trust Badges:
- Badge 1: {trust_badge_1}
- Badge 2: {trust_badge_2}""",
            placeholders={
                "store_name": "Store name",
                "hero_headline": "Main headline",
                "hero_subheadline": "Supporting text",
                "hero_cta": "Call to action",
                "hero_background": "Background description",
                "feature_1": "First feature",
                "feature_2": "Second feature",
                "feature_3": "Third feature",
                "testimonial": "Customer testimonial",
                "rating": "Rating",
                "trust_badge_1": "First trust badge",
                "trust_badge_2": "Second trust badge"
            },
            config={"sections": ["hero", "features", "testimonials", "trust"]}
        )
        
        # Product Page Template
        self._templates["product_page"] = PageTemplate(
            name="product_page",
            version="1.0",
            template="""Product Page for {product_name}

Hero Section:
- Product Name: {product_name}
- Tagline: {product_tagline}
- Price: {price}
- CTA: {product_cta}

Features Section:
- Feature 1: {product_feature_1}
- Feature 2: {product_feature_2}
- Feature 3: {product_feature_3}

Specs Section:
- Spec 1: {spec_1}
- Spec 2: {spec_2}

Reviews Section:
- Customer reviews for {product_name}

FAQ Section:
- FAQ 1: {faq_1}
- FAQ 2: {faq_2}

Related Products:
- Related to {product_name}""",
            placeholders={
                "product_name": "Product name",
                "product_tagline": "Product tagline",
                "price": "Product price",
                "product_cta": "Call to action",
                "product_feature_1": "First feature",
                "product_feature_2": "Second feature",
                "product_feature_3": "Third feature",
                "spec_1": "First specification",
                "spec_2": "Second specification",
                "faq_1": "First FAQ",
                "faq_2": "Second FAQ"
            },
            config={"sections": ["hero", "features", "specs", "reviews", "faq", "related"]}
        )
        
        # About Page Template
        self._templates["about"] = PageTemplate(
            name="about",
            version="1.0",
            template="""About Page for {store_name}

Brand Story:
- Story: {brand_story}
- Mission: {mission}
- Vision: {vision}

Values:
- Value 1: {value_1}
- Value 2: {value_2}
- Value 3: {value_3}

Team:
- Team member: {team_member}

Timeline:
- Founded: {founded_date}
- Milestone: {milestone}""",
            placeholders={
                "store_name": "Store name",
                "brand_story": "Brand story",
                "mission": "Mission statement",
                "vision": "Vision statement",
                "value_1": "First value",
                "value_2": "Second value",
                "value_3": "Third value",
                "team_member": "Team member",
                "founded_date": "Founding date",
                "milestone": "Milestone"
            },
            config={"sections": ["story", "values", "team", "timeline"]}
        )
        
        # Contact Page Template
        self._templates["contact"] = PageTemplate(
            name="contact",
            version="1.0",
            template="""Contact Page for {store_name}

Contact Information:
- Email: {email}
- Phone: {phone}
- Address: {address}

Contact Form:
- Form fields: {form_fields}

Business Hours:
- Hours: {business_hours}

Social Links:
- Social link: {social_link}""",
            placeholders={
                "store_name": "Store name",
                "email": "Contact email",
                "phone": "Contact phone",
                "address": "Business address",
                "form_fields": "Form fields",
                "business_hours": "Business hours",
                "social_link": "Social media link"
            },
            config={"sections": ["info", "form", "hours", "social"]}
        )
    
    def get_template(self, name: str) -> Optional[PageTemplate]:
        """Get a template by name."""
        return self._templates.get(name)
    
    def render_template(self, name: str, **kwargs) -> str:
        """Render a template with provided values."""
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template '{name}' not found")
        
        rendered = template.template
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            if placeholder in rendered:
                rendered = rendered.replace(placeholder, str(value))
        
        return rendered
    
    def list_templates(self) -> list:
        """List all available template names."""
        return list(self._templates.keys())


# Global template library instance
template_library = TemplateLibrary()
