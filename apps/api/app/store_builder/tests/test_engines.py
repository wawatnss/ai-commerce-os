"""
Unit Tests for Store Builder

Tests the store generation engines and validator.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.store_builder.engines import HomepageEngine, ThemeEngine, StoreValidator


class TestHomepageEngine:
    """Tests for HomepageEngine."""
    
    @pytest.fixture
    def engine(self):
        return HomepageEngine()
    
    @pytest.mark.asyncio
    async def test_generation(self, engine):
        """Test homepage generation."""
        context = {
            "brand_profile": {
                "brand_name": "TestStore",
                "slogan": "Quality Products",
                "mission": "To provide quality",
                "color_palette": {"primary": "#000000"},
                "differentiators": ["Quality", "Innovation"],
                "trust_elements": ["Guarantee"]
            },
            "product_data": {
                "product_name": "Test Product",
                "category": "electronics"
            }
        }
        
        result = await engine.generate(context)
        
        assert result.success is True
        assert "sections" in result.data
        assert len(result.data["sections"]) > 0


class TestThemeEngine:
    """Tests for ThemeEngine."""
    
    @pytest.fixture
    def engine(self):
        return ThemeEngine()
    
    @pytest.mark.asyncio
    async def test_generation(self, engine):
        """Test theme generation."""
        context = {
            "brand_profile": {
                "color_palette": {
                    "primary": {"hex": "#2563EB"},
                    "secondary": {"hex": "#10B981"},
                    "accent": {"hex": "#F59E0B"}
                },
                "typography": {
                    "heading": {"font": "Inter"},
                    "body": {"font": "Inter"}
                }
            }
        }
        
        result = await engine.generate(context)
        
        assert result.success is True
        assert "theme" in result.data
        assert "primary_color" in result.data["theme"]


class TestStoreValidator:
    """Tests for StoreValidator."""
    
    @pytest.fixture
    def validator(self):
        return StoreValidator()
    
    def test_validate_complete_store(self, validator):
        """Test validation of complete store."""
        store_blueprint = {
            "store_name": "TestStore",
            "store_description": "Quality products",
            "homepage": [{"section_type": "hero"}],
            "navigation": {"main_menu": []},
            "footer": {"columns": []},
            "theme": {"primary_color": "#000000", "dark_mode_enabled": True},
            "seo": {"title_template": "Test", "meta_description_template": "Test", "keywords": []}
        }
        
        result = validator.validate(store_blueprint)
        
        assert 0 <= result.overall_score <= 100
        assert len(result.strengths) + len(result.weaknesses) > 0
    
    def test_validate_incomplete_store(self, validator):
        """Test validation of incomplete store."""
        store_blueprint = {
            "store_name": "TestStore"
        }
        
        result = validator.validate(store_blueprint)
        
        assert result.overall_score <= 70
        assert len(result.weaknesses) > 0
