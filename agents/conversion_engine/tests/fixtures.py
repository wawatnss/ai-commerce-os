"""Shared test fixtures - representative store blueprints."""

import copy
from typing import Any, Dict


def minimal_blueprint() -> Dict[str, Any]:
    """A bare-bones blueprint, missing almost everything an optimizer should add."""
    return {
        "brand_profile_id": "1",
        "product_id": "demo-aaaaaaaa",
        "supplier_id": "demo-supplier-aaaaaaaa",
        "store_name": "Aurora Wireless Earbuds Co",
        "store_description": "Premium wireless earbuds for people on the move.",
        "tagline": "Sound, unleashed.",
        "homepage": [],
        "navigation": {"main_menu": [{"label": "Home", "link": "/"}]},
        "footer": {"columns": [], "copyright": "\u00a9 2026"},
        "theme": {"primary_color": "#2563EB"},
        "seo": {},
        "policies": {},
        "faq": [],
        "trust_badges": [],
    }


def realistic_blueprint() -> Dict[str, Any]:
    """A blueprint shaped like the real output of apps/api's Store Builder."""
    return {
        "brand_profile_id": "1",
        "product_id": "demo-b67623ef",
        "supplier_id": "demo-supplier-b67623ef",
        "store_name": "Solstice Ceramic Plant Pot Pro",
        "store_description": "To provide exceptional home-goods that enhance customers' lives",
        "tagline": "Quality Products for Everyone",
        "homepage": [
            {
                "section_type": "hero",
                "title": "Quality Products for Everyone",
                "content": {
                    "headline": "Discover Solstice Ceramic Plant Pot Pro",
                    "subheadline": "To provide exceptional home-goods that enhance customers' lives",
                    "cta": "Shop Now",
                    "background": "#2563EB",
                },
                "order": 0,
                "enabled": True,
            },
            {
                "section_type": "features",
                "title": "Why Choose Us",
                "content": {"features": ["Superior quality materials", "Innovative design", "Customer Service"]},
                "order": 1,
                "enabled": True,
            },
            {
                "section_type": "testimonials",
                "title": "What Our Customers Say",
                "content": {"testimonial": "Great products and excellent service!", "rating": 5},
                "order": 2,
                "enabled": True,
            },
            {
                "section_type": "trust",
                "title": "Trust Badges",
                "content": {"badges": ["Customer testimonials", "Money-back guarantee", "Secure checkout"]},
                "order": 3,
                "enabled": True,
            },
        ],
        "navigation": {
            "main_menu": [
                {"label": "Home", "link": "/"},
                {"label": "Shop", "link": "/shop"},
                {"label": "About", "link": "/about"},
            ],
        },
        "footer": {"columns": [], "copyright": "\u00a9 2026 Solstice Ceramic Plant Pot Pro. All rights reserved."},
        "theme": {
            "primary_color": "#2563EB",
            "secondary_color": "#10B981",
            "accent_color": "#F59E0B",
            "background_color": "#FFFFFF",
            "text_color": "#1F2937",
            "border_radius": "8px",
            "font_family": "Inter",
            "spacing": "comfortable",
            "animations_enabled": True,
            "dark_mode_enabled": True,
        },
        "seo": {
            "title_template": "Solstice Ceramic Plant Pot Pro | Best home-goods",
            "meta_description_template": "Discover the best home-goods at Solstice Ceramic Plant Pot Pro.",
            "keywords": ["home-goods", "quality"],
        },
        "policies": {
            "refund_policy": {"title": "Refund Policy", "days": 30, "process": "Contact support"},
            "shipping_policy": {
                "title": "Shipping Policy",
                "free_shipping_threshold": 50,
                "shipping_times": {"standard": "5-7 business days"},
            },
        },
        "faq": [],
        "trust_badges": ["Customer testimonials", "Money-back guarantee", "Secure checkout"],
        "reviews": [],
    }


def clone(blueprint: Dict[str, Any]) -> Dict[str, Any]:
    return copy.deepcopy(blueprint)
