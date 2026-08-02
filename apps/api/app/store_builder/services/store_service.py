"""
Store Builder Service

This module provides the main service layer for store generation operations.
It integrates with all previous intelligence engines.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..engines import (
    HomepageEngine,
    NavigationEngine,
    ThemeEngine,
    SEOEngine,
    PolicyEngine,
    StoreValidator
)
from ..repositories.store_repository import StoreRepository
from ..cache.store_cache import StoreCache
from ..schemas.store import StoreResponse, StoreCreateRequest, StoreValidationResponse
from ai_providers import AIProviderFactory


class StoreService:
    """Main service for store generation operations."""
    
    def __init__(self, db: Session):
        """Initialize the store service."""
        self.db = db
        self.repository = StoreRepository(db)
        self.cache = StoreCache()
        self.validator = StoreValidator()
        
        # Initialize engines
        self.engines = {
            "homepage": HomepageEngine(),
            "navigation": NavigationEngine(),
            "theme": ThemeEngine(),
            "seo": SEOEngine(),
            "policy": PolicyEngine()
        }
    
    async def generate_store(self, request: StoreCreateRequest) -> StoreResponse:
        """
        Generate a complete store blueprint.
        
        Integrates with Brand Builder, Product Intelligence, and Supplier Intelligence.
        """
        # Check cache first
        if not request.force_regenerate:
            cached = self.cache.get_store(request.product_id)
            if cached:
                return StoreResponse(**cached)
        
        # Get brand profile
        brand_profile = await self._get_brand_profile(request.brand_profile_id)
        if not brand_profile:
            raise ValueError(f"Brand profile {request.brand_profile_id} not found")
        
        # Get product intelligence data
        product_data = await self._get_product_intelligence(request.product_id)
        if not product_data:
            raise ValueError(f"Product intelligence not found for {request.product_id}")
        
        # Get supplier intelligence data (optional)
        supplier_data = None
        if request.supplier_id:
            supplier_data = await self._get_supplier_intelligence(request.supplier_id)
        
        # Prepare context for engines
        context = self._prepare_context(brand_profile, product_data, supplier_data)
        
        # Run all engines
        engine_results = {}
        for engine_name, engine in self.engines.items():
            if request.use_ai:
                ai_provider = AIProviderFactory.get_provider("openai")
                engine.ai_provider = ai_provider
            
            result = await engine.generate(context)
            engine_results[engine_name] = result
        
        # Compile store blueprint
        store_blueprint = self._compile_store_blueprint(engine_results, context)
        
        # Preserve the real identifiers from the request (compilation above derives
        # display-friendly defaults from the brand/product names, not the actual IDs)
        store_blueprint["brand_profile_id"] = request.brand_profile_id
        store_blueprint["product_id"] = request.product_id
        store_blueprint["supplier_id"] = request.supplier_id
        
        # Validate store (operates on the flat blueprint structure)
        validation_result = self.validator.validate(store_blueprint)
        store_blueprint["validation_result"] = validation_result.dict()
        store_blueprint["validation_score"] = validation_result.overall_score
        
        # Add metadata
        store_blueprint["metadata"] = {
            "brand_profile_id": request.brand_profile_id,
            "product_id": request.product_id,
            "supplier_id": request.supplier_id,
            "engines_used": list(engine_results.keys()),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Save to database
        existing = self.repository.get_store_by_product(request.product_id)
        if existing and not request.force_regenerate:
            return StoreResponse.from_orm(existing)
        
        if existing:
            self.repository.delete_store(existing.id)
        
        # The repository persists the full generated content under
        # `blueprint_json` (consumed as-is by apps/store-renderer), while the
        # top-level columns stay flat/queryable.
        persisted_data = {
            "user_id": request.user_id,
            "brand_profile_id": store_blueprint["brand_profile_id"],
            "product_id": store_blueprint["product_id"],
            "supplier_id": store_blueprint.get("supplier_id"),
            "store_name": store_blueprint["store_name"],
            "store_description": store_blueprint["store_description"],
            "tagline": store_blueprint.get("tagline"),
            "blueprint_json": store_blueprint,
            "validation_score": store_blueprint["validation_score"],
            "validation_result": store_blueprint["validation_result"],
            "metadata": store_blueprint["metadata"],
        }
        
        saved_store = self.repository.create_store(persisted_data)
        
        # Cache the result
        self.cache.set_store(request.product_id, saved_store.to_dict())
        
        return StoreResponse.from_orm(saved_store)
    
    async def _get_brand_profile(self, brand_profile_id: str) -> Optional[Dict[str, Any]]:
        """Get brand profile from Brand Builder, falling back to demo/mock data."""
        from app.brand_builder.repositories.brand_repository import BrandRepository
        
        try:
            brand = BrandRepository(self.db).get_brand_by_id(int(brand_profile_id))
        except (TypeError, ValueError):
            brand = None
        
        if brand:
            return {
                "brand_name": brand.brand_name,
                "slogan": brand.slogan,
                "mission": brand.mission,
                "vision": brand.vision,
                "color_palette": brand.color_palette or {},
                "typography": brand.typography or {},
                "differentiators": brand.differentiators or [],
                "trust_elements": brand.trust_elements or []
            }
        
        # Fallback mock data (used when no brand row is found, e.g. quick manual testing)
        return {
            "brand_name": "QualityStore",
            "slogan": "Quality Products for Everyone",
            "mission": "To provide exceptional products",
            "vision": "To become the leading provider",
            "color_palette": {
                "primary": {"hex": "#2563EB", "name": "Royal Blue"},
                "secondary": {"hex": "#10B981", "name": "Emerald"},
                "accent": {"hex": "#F59E0B", "name": "Amber"}
            },
            "typography": {
                "heading": {"font": "Inter", "weight": "700"},
                "body": {"font": "Inter", "weight": "400"}
            },
            "differentiators": ["Quality", "Innovation", "Service"],
            "trust_elements": ["Quality Guarantee", "Secure Checkout"]
        }
    
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
            "vibe": "modern"
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
    
    def _prepare_context(self, brand_profile: Dict[str, Any], product_data: Dict[str, Any], supplier_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare context for engines."""
        return {
            "brand_profile": brand_profile,
            "product_data": product_data,
            "supplier_data": supplier_data or {}
        }
    
    def _compile_store_blueprint(self, engine_results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Compile store blueprint from engine results."""
        blueprint_data = {
            "brand_profile_id": context["brand_profile"].get("brand_name", "1"),
            "product_id": context["product_data"].get("product_name", "1"),
            "supplier_id": context["supplier_data"].get("supplier_name") if context.get("supplier_data") else None,
            "store_name": context["brand_profile"].get("brand_name", "Store"),
            "store_description": context["brand_profile"].get("mission", "Quality products for everyone"),
            "tagline": context["brand_profile"].get("slogan", "Quality Products for Everyone")
        }
        
        # Add engine results
        if "homepage" in engine_results and engine_results["homepage"].success:
            blueprint_data["homepage"] = engine_results["homepage"].data.get("sections", [])
        
        if "navigation" in engine_results and engine_results["navigation"].success:
            nav_data = engine_results["navigation"].data
            blueprint_data["navigation"] = nav_data.get("navigation", {})
            blueprint_data["footer"] = nav_data.get("footer", {})
        
        if "theme" in engine_results and engine_results["theme"].success:
            blueprint_data["theme"] = engine_results["theme"].data.get("theme", {})
        
        if "seo" in engine_results and engine_results["seo"].success:
            blueprint_data["seo"] = engine_results["seo"].data.get("seo", {})
        
        if "policy" in engine_results and engine_results["policy"].success:
            policy_data = engine_results["policy"].data.get("policies", {})
            blueprint_data["policies"] = policy_data
        
        # Add defaults for other fields
        blueprint_data["collections"] = []
        blueprint_data["landing_pages"] = []
        blueprint_data["faq"] = []
        blueprint_data["about"] = {}
        blueprint_data["contact"] = {}
        blueprint_data["testimonials"] = context["brand_profile"].get("trust_elements", [])
        blueprint_data["reviews"] = []
        blueprint_data["trust_badges"] = context["brand_profile"].get("trust_elements", [])
        blueprint_data["hero_sections"] = []
        blueprint_data["banners"] = []
        blueprint_data["emails"] = {}
        blueprint_data["social"] = {"enabled": True}
        blueprint_data["export_config"] = {"format": "json", "platform": "agnostic"}
        
        return blueprint_data
    
    def validate_store(self, store_id: int) -> StoreValidationResponse:
        """Validate an existing store blueprint."""
        store = self.repository.get_store_by_id(store_id)
        if not store:
            raise ValueError(f"Store {store_id} not found")
        
        validation_result = self.validator.validate(store.to_dict())
        return StoreValidationResponse(**validation_result.dict())
    
    def export_store(self, store_id: int) -> Dict[str, Any]:
        """Export a complete store blueprint as platform-agnostic JSON."""
        store = self.repository.get_store_by_id(store_id)
        if not store:
            raise ValueError(f"Store {store_id} not found")
        
        return {
            "store_blueprint": store.to_dict(),
            "export_format": "json",
            "platform_agnostic": True,
            "export_timestamp": datetime.utcnow().isoformat()
        }
