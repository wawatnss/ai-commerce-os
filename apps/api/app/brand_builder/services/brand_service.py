"""
Brand Builder Service

This module provides the main service layer for brand generation operations.
It integrates with Product Intelligence and Supplier Intelligence engines.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..engines import (
    NameEngine,
    AudienceEngine,
    IdentityEngine,
    VisualEngine,
    MessagingEngine,
    PositioningEngine
)
from ..engines.validator import BrandValidator
from ..repositories.brand_repository import BrandRepository
from ..cache.brand_cache import BrandCache
from ..schemas.brand import BrandResponse, BrandCreateRequest, ValidationResponse
from ai_providers import AIProviderFactory


class BrandService:
    """Main service for brand generation operations."""
    
    def __init__(self, db: Session):
        """Initialize the brand service."""
        self.db = db
        self.repository = BrandRepository(db)
        self.cache = BrandCache()
        self.validator = BrandValidator()
        
        # Initialize engines
        self.engines = {
            "name": NameEngine(),
            "audience": AudienceEngine(),
            "identity": IdentityEngine(),
            "visual": VisualEngine(),
            "messaging": MessagingEngine(),
            "positioning": PositioningEngine()
        }
    
    async def generate_brand(self, request: BrandCreateRequest) -> BrandResponse:
        """
        Generate a complete brand profile.
        
        Integrates with Product Intelligence and Supplier Intelligence data.
        """
        # Check cache first
        if not request.force_regenerate:
            cached = self.cache.get_brand(request.product_id)
            if cached:
                return BrandResponse(**cached)
        
        # Get product intelligence data
        product_data = await self._get_product_intelligence(request.product_id)
        if not product_data:
            raise ValueError(f"Product intelligence not found for {request.product_id}")
        
        # Get supplier intelligence data (optional)
        supplier_data = None
        if request.supplier_id:
            supplier_data = await self._get_supplier_intelligence(request.supplier_id)
        
        # Prepare context for engines
        context = self._prepare_context(product_data, supplier_data)
        
        # Run all engines
        engine_results = {}
        for engine_name, engine in self.engines.items():
            if request.use_ai:
                # Initialize AI provider
                ai_provider = AIProviderFactory.get_provider("openai")
                engine.ai_provider = ai_provider
            
            result = await engine.generate(context)
            engine_results[engine_name] = result
        
        # Compile brand profile
        brand_profile = self._compile_brand_profile(engine_results, context)
        brand_profile["product_id"] = request.product_id
        brand_profile["supplier_id"] = request.supplier_id
        
        # Validate brand
        validation_result = self.validator.validate(brand_profile)
        brand_profile["validation_result"] = validation_result.dict()
        brand_profile["confidence_score"] = validation_result.overall_score
        
        # Add metadata
        brand_profile["metadata"] = {
            "product_id": request.product_id,
            "supplier_id": request.supplier_id,
            "engines_used": list(engine_results.keys()),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Save to database
        existing = self.repository.get_brand_by_product(request.product_id)
        if existing and not request.force_regenerate:
            return BrandResponse.from_orm(existing)
        
        if existing:
            self.repository.delete_brand(existing.id)
        
        saved_brand = self.repository.create_brand(brand_profile)
        
        # Cache the result
        self.cache.set_brand(request.product_id, saved_brand.to_dict())
        
        return BrandResponse.from_orm(saved_brand)
    
    async def _get_product_intelligence(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product intelligence data, falling back to demo/mock data."""
        from app.product_intelligence.repositories.product_repository import ProductRepository
        
        report = ProductRepository(self.db).get_report_by_trend_id(product_id)
        if report:
            return {
                "product_name": report.product_name,
                "category": report.category,
                "target_audience": f"{report.category} enthusiasts",
                "unique_value": "quality and innovation",
                "vibe": "modern",
                "overall_score": report.overall_score
            }
        
        # Fallback mock data (used when no product intelligence report is found)
        return {
            "product_name": "Sample Product",
            "category": "electronics",
            "target_audience": "tech enthusiasts",
            "unique_value": "innovation",
            "vibe": "modern",
            "overall_score": 75
        }
    
    async def _get_supplier_intelligence(self, supplier_id: str) -> Optional[Dict[str, Any]]:
        """Get supplier intelligence data, falling back to demo/mock data."""
        from app.supplier_intelligence.repositories.supplier_repository import SupplierRepository
        
        supplier = SupplierRepository(self.db).get_supplier_by_id(supplier_id)
        if supplier:
            return {
                "supplier_name": supplier.name,
                "country": supplier.country,
                "reliability_score": 80
            }
        
        # Fallback mock data (used when no supplier row is found)
        return {
            "supplier_name": "Quality Supplier",
            "country": "China",
            "reliability_score": 80
        }
    
    def _prepare_context(self, product_data: Dict[str, Any], supplier_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare context for brand engines."""
        context = {
            "product_name": product_data.get("product_name", "Product"),
            "category": product_data.get("category", "General"),
            "target_audience": product_data.get("target_audience", "General consumers"),
            "unique_value": product_data.get("unique_value", "Quality"),
            "vibe": product_data.get("vibe", "Modern"),
            "brand_values": "quality, innovation, customer satisfaction"
        }
        
        if supplier_data:
            context["supplier_country"] = supplier_data.get("country")
            context["supplier_reliability"] = supplier_data.get("reliability_score")
        
        return context
    
    def _compile_brand_profile(self, engine_results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Compile brand profile from engine results."""
        profile = {}
        
        # Name
        if "name" in engine_results and engine_results["name"].success:
            name_data = engine_results["name"].data
            profile["brand_name"] = name_data.get("selected", context["product_name"])
        
        # Audience
        if "audience" in engine_results and engine_results["audience"].success:
            profile["customer_persona"] = engine_results["audience"].data.get("persona", {})
            profile["target_audience"] = context["target_audience"]
        
        # Identity
        if "identity" in engine_results and engine_results["identity"].success:
            identity = engine_results["identity"].data.get("identity", {})
            profile["mission"] = identity.get("mission")
            profile["vision"] = identity.get("vision")
        
        # Visual
        if "visual" in engine_results and engine_results["visual"].success:
            visual = engine_results["visual"].data
            profile["color_palette"] = visual.get("color_palette", {})
            profile["typography"] = visual.get("typography", {})
            profile["logo_prompt"] = visual.get("logo_prompt")
            profile["packaging_prompt"] = visual.get("packaging_prompt")
            profile["product_photography_prompt"] = visual.get("product_photography_prompt")
            profile["hero_banner_prompt"] = visual.get("hero_banner_prompt")
        
        # Messaging
        if "messaging" in engine_results and engine_results["messaging"].success:
            messaging = engine_results["messaging"].data
            profile["tone_of_voice"] = messaging.get("tone_of_voice", {}).get("primary")
            profile["writing_style"] = messaging.get("writing_style", {})
            profile["social_media_style"] = messaging.get("social_media_style")
            profile["seo_style"] = messaging.get("seo_style")
            profile["email_style"] = messaging.get("email_style")
        
        # Positioning
        if "positioning" in engine_results and engine_results["positioning"].success:
            positioning = engine_results["positioning"].data
            profile["unique_value_proposition"] = positioning.get("unique_value_proposition", {})
            profile["differentiators"] = positioning.get("differentiators", [])
            profile["trust_elements"] = positioning.get("trust_elements", [])
            profile["domain_name_suggestions"] = positioning.get("domain_name_suggestions", [])
        
        return profile
    
    def validate_brand(self, brand_id: int) -> ValidationResponse:
        """Validate an existing brand profile."""
        brand = self.repository.get_brand_by_id(brand_id)
        if not brand:
            raise ValueError(f"Brand {brand_id} not found")
        
        validation_result = self.validator.validate(brand.to_dict())
        return ValidationResponse(**validation_result.dict())
    
    def export_brand(self, brand_id: int) -> Dict[str, Any]:
        """Export a complete brand profile as JSON."""
        brand = self.repository.get_brand_by_id(brand_id)
        if not brand:
            raise ValueError(f"Brand {brand_id} not found")
        
        return {
            "brand_profile": brand.to_dict(),
            "export_timestamp": datetime.utcnow().isoformat()
        }
