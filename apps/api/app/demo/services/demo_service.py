"""
Demo Service

Orchestrates a full, self-contained run of the platform pipeline:

    Trend -> Product -> Supplier -> Brand -> Store -> Preview

Everything runs in rule-based / mock mode (use_ai=False, mock supplier data),
so this never calls OpenAI, Anthropic, or any other external API. It only
needs the local database (Postgres in production, SQLite when run directly
for quick manual testing, see seed_demo.py).
"""

import inspect
import time
import uuid
from datetime import datetime
from typing import Awaitable, Callable, List, Union

from sqlalchemy.orm import Session

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
from app.store_builder.schemas.store import StoreCreateRequest

from ..schemas.demo import DemoGenerateResponse, DemoStep, DemoStepStatus

# A small pool of fictional products so repeated demo runs feel varied.
DEMO_PRODUCTS = [
    {
        "product_name": "Aurora Wireless Earbuds",
        "category": "electronics",
        "tags": ["audio", "wireless", "earbuds"],
    },
    {
        "product_name": "Solstice Ceramic Plant Pot",
        "category": "home-goods",
        "tags": ["home", "plants", "decor"],
    },
    {
        "product_name": "Nimbus Foldable Yoga Mat",
        "category": "fitness",
        "tags": ["fitness", "yoga", "wellness"],
    },
]


class DemoService:
    """Runs the full demo pipeline and reports progress step by step."""

    def __init__(self, db: Session):
        self.db = db
        self.steps: List[DemoStep] = []

    async def generate(self) -> DemoGenerateResponse:
        run_id = uuid.uuid4().hex[:8]
        product_seed = DEMO_PRODUCTS[int(run_id, 16) % len(DEMO_PRODUCTS)]

        trend_id = f"demo-{run_id}"
        supplier_id = f"demo-supplier-{run_id}"

        try:
            # 1. Trend detected
            await self._step("trend_detected", "Trend detected", lambda: TrendService(self.db).create_trend(
                TrendItemCreate(
                    trend_id=trend_id,
                    source="demo",
                    product_name=product_seed["product_name"],
                    category=product_seed["category"],
                    tags=product_seed["tags"],
                    popularity_score=82,
                    growth_score=74,
                    competition_score=38,
                    opportunity_score=79,
                    confidence_score=88,
                    detected_at=datetime.utcnow(),
                    metadata={"demo": True, "run_id": run_id},
                )
            ))

            # 2. Product evaluated
            product_report = await self._step(
                "product_evaluated",
                "Product evaluated",
                lambda: ProductService(self.db).analyze_product(trend_id, force_reanalyze=True),
            )

            # 3. Supplier selected
            await self._step(
                "supplier_selected",
                "Supplier selected",
                lambda: self._select_supplier(trend_id, supplier_id),
            )

            # 4. Brand generated (use_ai=False -> fully rule-based, no external API)
            brand = await self._step(
                "brand_generated",
                "Brand generated",
                lambda: BrandService(self.db).generate_brand(BrandCreateRequest(
                    product_id=trend_id,
                    supplier_id=supplier_id,
                    force_regenerate=True,
                    use_ai=False,
                )),
            )

            # 5. Store generated (use_ai=False -> fully rule-based, no external API)
            store = await self._step(
                "store_generated",
                "Store generated",
                lambda: StoreService(self.db).generate_store(StoreCreateRequest(
                    brand_profile_id=str(brand.id),
                    product_id=trend_id,
                    supplier_id=supplier_id,
                    force_regenerate=True,
                    use_ai=False,
                )),
            )

            # 6. Preview ready
            await self._step(
                "preview_ready",
                "Preview ready",
                lambda: StoreService(self.db).repository.get_store_by_id(store.id),
            )

            return DemoGenerateResponse(
                success=True,
                steps=self.steps,
                trend_id=trend_id,
                product_report_id=product_report.id,
                supplier_id=supplier_id,
                brand_id=brand.id,
                store_id=store.id,
            )

        except Exception as exc:  # noqa: BLE001 - surfaced to the caller via the response
            return DemoGenerateResponse(
                success=False,
                steps=self.steps,
                trend_id=trend_id,
                error=str(exc),
            )

    def _select_supplier(self, trend_id: str, supplier_id: str):
        """Create a demo supplier + offer, then evaluate it (rule-based scoring)."""
        supplier_service = SupplierService(self.db)
        supplier_service.create_supplier(SupplierCreate(
            supplier_id=supplier_id,
            name="Demo Global Supply Co.",
            source="demo",
            country="Vietnam",
            currency="USD",
            contact={"email": "sales@demo-supplier.example"},
            metadata={"tier": "standard", "demo": True},
        ).dict())

        offer = SupplierOfferCreate(
            supplier_id=supplier_id,
            product_id=trend_id,
            unit_cost=8.5,
            minimum_order_quantity=100,
            estimated_processing_time=3,
            estimated_shipping_time=12,
            available_quantity=5000,
            currency="USD",
            metadata={"demo": True},
        )
        supplier_service.repository.create_offer(offer.dict())

        return supplier_service.evaluate_supplier(EvaluationRequest(
            supplier_id=supplier_id,
            product_id=trend_id,
            force_reevaluate=True,
        ))

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
            self.steps.append(DemoStep(
                key=key,
                label=label,
                status=DemoStepStatus.COMPLETED,
                duration_ms=duration_ms,
            ))
            return result
        except Exception as exc:  # noqa: BLE001 - re-raised after being recorded
            duration_ms = int((time.perf_counter() - start) * 1000)
            self.steps.append(DemoStep(
                key=key,
                label=label,
                status=DemoStepStatus.FAILED,
                detail=str(exc),
                duration_ms=duration_ms,
            ))
            raise
