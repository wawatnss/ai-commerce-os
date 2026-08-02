"""
Unit Tests for Brand Builder

Tests the brand generation engines and validator.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.brand_builder.engines import NameEngine, AudienceEngine, BrandValidator


class TestNameEngine:
    """Tests for NameEngine."""
    
    @pytest.fixture
    def engine(self):
        return NameEngine()
    
    @pytest.mark.asyncio
    async def test_mock_generation(self, engine):
        """Test mock name generation."""
        context = {
            "product_name": "Test Product",
            "category": "electronics",
            "target_audience": "tech enthusiasts"
        }
        
        result = await engine.generate(context)
        
        assert result.success is True
        assert "suggestions" in result.data
        assert len(result.data["suggestions"]) > 0


class TestAudienceEngine:
    """Tests for AudienceEngine."""
    
    @pytest.fixture
    def engine(self):
        return AudienceEngine()
    
    @pytest.mark.asyncio
    async def test_mock_generation(self, engine):
        """Test mock audience generation."""
        context = {
            "product_name": "Test Product",
            "category": "electronics",
            "target_audience": "tech enthusiasts"
        }
        
        result = await engine.generate(context)
        
        assert result.success is True
        assert "persona" in result.data


class TestBrandValidator:
    """Tests for BrandValidator."""
    
    @pytest.fixture
    def validator(self):
        return BrandValidator()
    
    def test_validate_complete_brand(self, validator):
        """Test validation of complete brand profile."""
        brand_profile = {
            "brand_name": "TestBrand",
            "mission": "To provide quality products",
            "vision": "To be the best",
            "color_palette": {"primary": "#000000"},
            "tone_of_voice": "professional",
            "target_audience": "professionals",
            "unique_value_proposition": {"statement": "Best products"},
            "differentiators": ["Quality", "Service"]
        }
        
        result = validator.validate(brand_profile)
        
        assert 0 <= result.overall_score <= 100
        assert len(result.strengths) + len(result.weaknesses) > 0
    
    def test_validate_incomplete_brand(self, validator):
        """Test validation of incomplete brand profile."""
        brand_profile = {
            "brand_name": "TestBrand"
        }
        
        result = validator.validate(brand_profile)
        
        assert result.overall_score < 70
        assert len(result.weaknesses) > 0
