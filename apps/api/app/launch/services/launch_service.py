"""
Launch Service

Orchestrates a full run of the platform pipeline from real user input:

    Trend -> Product -> Supplier -> Brand -> Store -> Optimize -> Done

This mirrors app.demo.services.demo_service.DemoService, but:
- Uses the name/category/objective/budget provided by the "Create a new
  brand" wizard instead of a random demo product.
- Never enables demo-only shortcuts (e.g. ReviewOptimizer's simulated
  ratings) since this produces a brand a real user asked for.
- Also runs the Phase 8 Conversion Optimization Engine as an explicit
  "Optimisation" step, matching the wizard's progress bar
  (Recherche / Produits / Marque / Boutique / Optimisation / Termine).
"""

import inspect
import time
import uuid
from datetime import datetime
from typing import Awaitable, Callable, List, Optional, Union

from sqlalchemy.orm import Session

from agents.conversion_engine import ConversionEngine

from app.trend_intelligence.services.trend_service import TrendService
from app.trend_intelligence.schemas.trend import TrendItemCreate
from app.product_intelligence.services.product_service import ProductService
from app.supplier_intelligence.services.supplier_service import SupplierService
from app.supplier_intelligence.schemas.supplier import (
    SupplierCreate,
    SupplierOfferCreate,
    EvaluationRequest,
)
from app.brand_builder.services.brand_service import BrandService
from app.brand_builder.schemas.brand import BrandCreateRequest
from app.store_builder.services.store_service import StoreService
from app.store_builder.services.readiness import ReadinessEngine
from app.store_builder.services.shopify_readiness import ShopifyReadinessEngine
from app.launch.services.product_content import get_product_content
from agents.visual_identity.engines import VisualIdentityEngine
from agents.cta_engine.engines import CTAEngine
from agents.faq_engine.engines import FAQEngine
from app.store_builder.schemas.store import StoreCreateRequest

from ..schemas.launch import LaunchRequest, LaunchResponse, LaunchStep, LaunchStepStatus, BudgetTier

# Starting budget bracket -> initial supplier offer sizing. These are
# reasonable, transparent defaults (not real market data) used purely to
# seed the rule-based supplier evaluation; they are never presented to the
# end customer as real pricing.
BUDGET_TIERS = {
    BudgetTier.STARTER: {"unit_cost": 12.0, "moq": 50, "processing_days": 5, "shipping_days": 15, "available": 1000},
    BudgetTier.GROWTH: {"unit_cost": 8.5, "moq": 100, "processing_days": 3, "shipping_days": 10, "available": 5000},
    BudgetTier.SCALE: {"unit_cost": 5.0, "moq": 500, "processing_days": 2, "shipping_days": 7, "available": 20000},
}


class LaunchService:
    """Runs the "create a new brand" pipeline and reports progress step by step."""

    def __init__(self, db: Session):
        self.db = db
        self.steps: List[LaunchStep] = []

    async def generate(self, request: LaunchRequest, user_id: Optional[int] = None) -> LaunchResponse:
        run_id = uuid.uuid4().hex[:8]
        trend_id = f"launch-{run_id}"
        supplier_id = f"launch-supplier-{run_id}"

        try:
            # 1. Recherche (trend detected)
            await self._step("research", "Recherche", lambda: TrendService(self.db).create_trend(
                TrendItemCreate(
                    trend_id=trend_id,
                    source="launch",
                    product_name=request.name,
                    category=request.category,
                    tags=[request.category, request.objective.value],
                    popularity_score=80,
                    growth_score=72,
                    competition_score=40,
                    opportunity_score=76,
                    confidence_score=85,
                    detected_at=datetime.utcnow(),
                    metadata={
                        "launch": True,
                        "run_id": run_id,
                        "objective": request.objective.value,
                        "budget": request.budget.value,
                    },
                )
            ))

            # 2. Produits (product analysis + supplier selection)
            await self._step(
                "products",
                "Produits",
                lambda: self._analyze_products(trend_id, supplier_id, request.budget),
            )

            # 3. Marque (brand generated, rule-based - no external API)
            brand = await self._step(
                "brand",
                "Marque",
                lambda: BrandService(self.db).generate_brand(BrandCreateRequest(
                    product_id=trend_id,
                    supplier_id=supplier_id,
                    force_regenerate=True,
                    use_ai=False,
                )),
            )

            # 4. Boutique (store generated, rule-based - no external API)
            store = await self._step(
                "store",
                "Boutique",
                lambda: StoreService(self.db).generate_store(StoreCreateRequest(
                    brand_profile_id=str(brand.id),
                    product_id=trend_id,
                    supplier_id=supplier_id,
                    user_id=user_id,
                    force_regenerate=True,
                    use_ai=False,
                )),
            )

            # 5. Optimisation (Phase 8 Conversion Optimization Engine)
            await self._step(
                "optimization",
                "Optimisation",
                lambda: self._optimize_store(store.id),
            )

            # 6. Sprint 4: Visual identity, CTA and FAQ enrichment
            await self._step(
                "content",
                "Content & Identity",
                lambda: self._enrich_store(store.id, request.category),
            )

            # 7. Termine (preview ready)
            final_store = await self._step(
                "done",
                "Termine",
                lambda: StoreService(self.db).repository.get_store_by_id(store.id),
            )

            # Sprint 2.5: compute publication readiness from the final blueprint
            readiness = ReadinessEngine().run(final_store.blueprint_json or {})
            shopify = ShopifyReadinessEngine().run(final_store.blueprint_json or {})

            return LaunchResponse(
                success=True,
                steps=self.steps,
                trend_id=trend_id,
                supplier_id=supplier_id,
                brand_id=brand.id,
                store_id=store.id,
                store_name=final_store.store_name,
                readiness=readiness.model_dump(),
                shopify_readiness=shopify.model_dump(),
            )

        except Exception as exc:  # noqa: BLE001 - surfaced to the caller via the response
            return LaunchResponse(
                success=False,
                steps=self.steps,
                trend_id=trend_id,
                error=str(exc),
            )

    def _analyze_products(self, trend_id: str, supplier_id: str, budget: BudgetTier):
        """Analyze the product, then create + evaluate a supplier offer sized to the budget tier."""
        product_report = ProductService(self.db).analyze_product(trend_id, force_reanalyze=True)

        tier = BUDGET_TIERS[budget]
        supplier_service = SupplierService(self.db)
        supplier_service.create_supplier(SupplierCreate(
            supplier_id=supplier_id,
            name="Preferred Launch Partner",
            source="launch",
            country="Vietnam",
            currency="USD",
            contact={"email": "sales@launch-partner.example"},
            metadata={"tier": budget.value},
        ).dict())

        offer = SupplierOfferCreate(
            supplier_id=supplier_id,
            product_id=trend_id,
            unit_cost=tier["unit_cost"],
            minimum_order_quantity=tier["moq"],
            estimated_processing_time=tier["processing_days"],
            estimated_shipping_time=tier["shipping_days"],
            available_quantity=tier["available"],
            currency="USD",
            metadata={"budget_tier": budget.value},
        )
        supplier_service.repository.create_offer(offer.dict())
        supplier_service.evaluate_supplier(EvaluationRequest(
            supplier_id=supplier_id,
            product_id=trend_id,
            force_reevaluate=True,
        ))

        return product_report

    def _optimize_store(self, store_id: int):
        """Run the Conversion Optimization Engine and persist the result (never demo_mode)."""
        repository = StoreService(self.db).repository
        store = repository.get_store_by_id(store_id)
        optimized_blueprint, report = ConversionEngine().run(store.blueprint_json, demo_mode=False)
        repository.update_store(store_id, {"blueprint_json": optimized_blueprint})
        return report

    def _enrich_store(self, store_id: int, category: str):
        """Sprint 4: enrich blueprint with brand asset pack, contextual CTAs and diverse FAQ."""
        import copy
        repository = StoreService(self.db).repository
        store = repository.get_store_by_id(store_id)
        blueprint = copy.deepcopy(store.blueprint_json or {})

        # Ensure category is known by downstream engines
        product_page = blueprint.setdefault("product_page", {})
        product_page["category"] = product_page.get("category") or category

        cta_set = CTAEngine().run(blueprint)
        faq_set = FAQEngine().run(blueprint, blueprint.get("policies"))
        visual_pack = VisualIdentityEngine().run(blueprint)

        # Update homepage hero CTA
        homepage = blueprint.get("homepage", [])
        if isinstance(homepage, list):
            for section in homepage:
                if isinstance(section, dict) and section.get("section_type") == "hero":
                    content = section.get("content", {})
                    content["cta"] = cta_set.hero.label
                    section["content"] = content

        # Update product CTA and category-specific benefits/features
        product_page = blueprint.setdefault("product_page", {})
        product_page["cta"] = cta_set.product.label
        product_page["cta_variants"] = [v.dict() for v in cta_set.all_variants]

        brand = blueprint.get("store_name", "Brand")
        product = product_page.get("product_name") or product_page.get("product") or brand
        product_page.update(get_product_content(category, brand, product))

        # Update FAQ
        blueprint["faq"] = [it.dict() for it in faq_set.items]
        blueprint["faq_diversity_score"] = faq_set.diversity_score

        # Add brand asset pack
        blueprint["brand_asset_pack"] = visual_pack.dict()

        repository.update_store(store_id, {"blueprint_json": blueprint})
        return {"cta": cta_set.hero.label, "faq_count": len(faq_set.items)}

    async def _step(
        self,
        key: str,
        label: str,
        fn: Callable[[], Union[object, Awaitable[object]]],
    ):
        """
        Run a single pipeline step, recording its status/duration.

        `fn` may return either a plain value (sync services) or an awaitable
        (async services); both are supported transparently.
        """
        start = time.perf_counter()
        try:
            result = fn()
            if inspect.isawaitable(result):
                result = await result
            duration_ms = int((time.perf_counter() - start) * 1000)
            self.steps.append(LaunchStep(
                key=key,
                label=label,
                status=LaunchStepStatus.COMPLETED,
                duration_ms=duration_ms,
            ))
            return result
        except Exception as exc:  # noqa: BLE001 - re-raised after being recorded
            duration_ms = int((time.perf_counter() - start) * 1000)
            self.steps.append(LaunchStep(
                key=key,
                label=label,
                status=LaunchStepStatus.FAILED,
                detail=str(exc),
                duration_ms=duration_ms,
            ))
            raise
