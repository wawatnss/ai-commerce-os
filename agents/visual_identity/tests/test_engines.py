"""Tests for Visual Identity Engine."""

import pytest
from agents.visual_identity.engines import VisualIdentityEngine


def test_visual_identity_produces_brand_asset_pack():
    blueprint = {
        "store_name": "Nova Smart Hub",
        "store_description": "Experience the future of smart home living.",
        "product_page": {"category": "tech", "product_name": "Nova Smart Hub"},
        "theme": {
            "primary_color": "#3B82F6",
            "secondary_color": "#06B6D4",
            "accent_color": "#22C55E",
        },
    }
    pack = VisualIdentityEngine().run(blueprint)
    assert pack.branding.logo_svg.startswith("<svg")
    assert pack.branding.favicon_svg.startswith("<svg")
    assert len(pack.branding.palette) == 5
    assert pack.product.packshot.prompt
    assert pack.marketing.instagram_post.prompt


def test_visual_identity_uses_category_palette_fallback():
    blueprint = {
        "store_name": "Glow",
        "store_description": "Reveal your natural glow.",
        "product_page": {"category": "beauty"},
    }
    pack = VisualIdentityEngine().run(blueprint)
    assert pack.source_palette.startswith("category:")
    assert any(c.name == "Primary" for c in pack.branding.palette)
