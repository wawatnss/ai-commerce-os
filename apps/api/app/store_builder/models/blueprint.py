"""
Store Blueprint Model

This module defines the complete store blueprint structure.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SEOConfig(BaseModel):
    """SEO configuration for the store."""
    title_template: str
    meta_description_template: str
    keywords: List[str] = Field(default_factory=list)
    open_graph_enabled: bool = True
    twitter_card_enabled: bool = True
    structured_data_enabled: bool = True


class SocialConfig(BaseModel):
    """Social media configuration."""
    facebook_enabled: bool = True
    instagram_enabled: bool = True
    twitter_enabled: bool = True
    pinterest_enabled: bool = True
    tiktok_enabled: bool = False


class ThemeConfig(BaseModel):
    """Theme configuration."""
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    text_color: str
    border_radius: str = "8px"
    font_family: str = "Inter"
    button_style: str = "modern"
    card_style: str = "clean"
    spacing: str = "comfortable"
    animations_enabled: bool = True
    dark_mode_enabled: bool = True


class HomepageSection(BaseModel):
    """Homepage section configuration."""
    section_type: str  # hero, features, testimonials, cta, etc.
    title: str
    content: Dict[str, Any] = Field(default_factory=dict)
    order: int = 0
    enabled: bool = True


class ProductPageConfig(BaseModel):
    """Product page configuration."""
    sections: List[str] = Field(default_factory=lambda: ["hero", "features", "reviews", "faq", "cta"])
    layout: str = "standard"  # standard, split, minimal
    show_related_products: bool = True
    show_reviews: bool = True
    show_faqs: bool = True


class PolicyConfig(BaseModel):
    """Policy configuration."""
    refund_policy: Dict[str, Any] = Field(default_factory=dict)
    shipping_policy: Dict[str, Any] = Field(default_factory=dict)
    privacy_policy: Dict[str, Any] = Field(default_factory=dict)
    terms_of_service: Dict[str, Any] = Field(default_factory=dict)


class EmailConfig(BaseModel):
    """Email configuration."""
    welcome_email: Dict[str, Any] = Field(default_factory=dict)
    order_confirmation: Dict[str, Any] = Field(default_factory=dict)
    shipping_notification: Dict[str, Any] = Field(default_factory=dict)
    abandoned_cart: Dict[str, Any] = Field(default_factory=dict)


class StoreBlueprint(BaseModel):
    """
    Complete store blueprint.
    
    This represents the complete configuration for an e-commerce store,
    generated from intelligence data and brand profile.
    """
    # Source Data
    brand_profile_id: str = Field(..., description="Brand profile ID")
    product_id: str = Field(..., description="Product ID")
    supplier_id: Optional[str] = Field(None, description="Supplier ID")
    
    # Store Identity
    store_name: str = Field(..., description="Store name")
    store_description: str = Field(..., description="Store description")
    tagline: str = Field(..., description="Store tagline")
    
    # Pages
    homepage: List[HomepageSection] = Field(default_factory=list)
    navigation: Dict[str, Any] = Field(default_factory=dict)
    footer: Dict[str, Any] = Field(default_factory=dict)
    
    # Product Pages
    product_pages: ProductPageConfig = Field(default_factory=ProductPageConfig)
    
    # Content Pages
    collections: List[Dict[str, Any]] = Field(default_factory=list)
    landing_pages: List[Dict[str, Any]] = Field(default_factory=list)
    faq: List[Dict[str, Any]] = Field(default_factory=list)
    policies: PolicyConfig = Field(default_factory=PolicyConfig)
    about: Dict[str, Any] = Field(default_factory=dict)
    contact: Dict[str, Any] = Field(default_factory=dict)
    
    # Trust Elements
    testimonials: List[Dict[str, Any]] = Field(default_factory=list)
    reviews: List[Dict[str, Any]] = Field(default_factory=list)
    trust_badges: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Visual Elements
    hero_sections: List[Dict[str, Any]] = Field(default_factory=list)
    banners: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Configuration
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    seo: SEOConfig = Field(default_factory=SEOConfig)
    social: SocialConfig = Field(default_factory=SocialConfig)
    emails: EmailConfig = Field(default_factory=EmailConfig)
    
    # Export Configuration
    export_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        schema_extra = "forbid"
