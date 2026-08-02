"""
Supplier Intelligence Service

This module provides the main service layer for supplier intelligence operations.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from ..engines import SupplierScoreEngine, ScoreWeights
from ..repositories.supplier_repository import SupplierRepository
from ..cache.supplier_cache import SupplierCache
from ..schemas.supplier import (
    SupplierResponse,
    SupplierOfferResponse,
    SupplierEvaluationResponse,
    EvaluationRequest,
    ComparisonRequest,
    ComparisonResponse,
    BestOffersResponse
)
from ..providers.mock_provider import MockSupplierProvider


class SupplierService:
    """Main service for supplier intelligence operations."""
    
    def __init__(self, db: Session):
        """Initialize the supplier service."""
        self.db = db
        self.repository = SupplierRepository(db)
        self.cache = SupplierCache()
        self.score_engine = SupplierScoreEngine()
        self.provider = MockSupplierProvider()
    
    def create_supplier(self, supplier_data: Dict[str, Any]) -> SupplierResponse:
        """Create a new supplier."""
        supplier = self.repository.create_supplier(supplier_data)
        return SupplierResponse.from_orm(supplier)
    
    def import_offers(self, product_id: str, supplier_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Import offers from providers."""
        offers = self.provider.collect_offers(product_id, supplier_ids)
        
        imported = 0
        for offer in offers:
            offer_data = offer.dict()
            self.repository.create_offer(offer_data)
            imported += 1
        
        # Invalidate cache
        self.cache.invalidate_product(product_id)
        
        return {
            "success": True,
            "imported": imported,
            "message": f"Imported {imported} offers"
        }
    
    def evaluate_supplier(self, request: EvaluationRequest) -> SupplierEvaluationResponse:
        """Evaluate a supplier for a product."""
        # Check cache first
        if not request.force_reevaluate:
            cached = self.cache.get_evaluation(request.supplier_id, request.product_id)
            if cached:
                return SupplierEvaluationResponse(**cached)
        
        # Get offer data
        from ..models.supplier import SupplierOffer
        offer = self.db.query(SupplierOffer).filter(
            SupplierOffer.supplier_id == request.supplier_id,
            SupplierOffer.product_id == request.product_id
        ).first()
        
        if not offer:
            raise ValueError(f"Offer not found for supplier {request.supplier_id} and product {request.product_id}")
        
        # Get supplier metadata
        supplier = self.repository.get_supplier_by_id(request.supplier_id)
        supplier_metadata = supplier.metadata if supplier else {}
        
        # Prepare offer data for evaluation
        offer_data = {
            "unit_cost": offer.unit_cost,
            "minimum_order_quantity": offer.minimum_order_quantity,
            "estimated_processing_time": offer.estimated_processing_time,
            "estimated_shipping_time": offer.estimated_shipping_time,
            "available_quantity": offer.available_quantity,
            "currency": offer.currency,
            "metadata": offer.metadata or {}
        }
        
        # Run evaluation
        score_result = self.score_engine.evaluate(offer_data, supplier_metadata)
        
        # Prepare evaluation data
        evaluation_data = {
            "supplier_id": request.supplier_id,
            "product_id": request.product_id,
            "cost_score": score_result.rule_results.get("cost", {}).get("score", 0),
            "delivery_score": score_result.rule_results.get("delivery", {}).get("score", 0),
            "moq_score": score_result.rule_results.get("moq", {}).get("score", 0),
            "availability_score": score_result.rule_results.get("availability", {}).get("score", 0),
            "reliability_score": score_result.rule_results.get("reliability", {}).get("score", 0),
            "flexibility_score": score_result.rule_results.get("flexibility", {}).get("score", 0),
            "data_quality_score": score_result.rule_results.get("data_quality", {}).get("score", 0),
            "overall_score": score_result.overall_score,
            "confidence_score": score_result.confidence_score,
            "recommendation": score_result.recommendation.value,
            "reasoning": score_result.reasoning,
            "strengths": score_result.strengths,
            "weaknesses": score_result.weaknesses,
            "rule_results": score_result.rule_results,
            "rule_config": score_result.metadata
        }
        
        # Create or update evaluation
        existing = self.repository.get_evaluation(request.supplier_id, request.product_id)
        if existing:
            self.db.delete(existing)
        
        evaluation = self.repository.create_evaluation(evaluation_data)
        
        # Cache the result
        self.cache.set_evaluation(request.supplier_id, request.product_id, evaluation.to_dict())
        
        return SupplierEvaluationResponse.from_orm(evaluation)
    
    def compare_suppliers(self, request: ComparisonRequest) -> ComparisonResponse:
        """Compare multiple suppliers for a product."""
        evaluations = []
        
        for supplier_id in request.supplier_ids:
            eval_request = EvaluationRequest(
                supplier_id=supplier_id,
                product_id=request.product_id,
                force_reevaluate=request.force_reevaluate
            )
            try:
                evaluation = self.evaluate_supplier(eval_request)
                evaluations.append(evaluation)
            except Exception:
                continue
        
        # Find best supplier
        best_supplier = max(evaluations, key=lambda e: e.overall_score) if evaluations else None
        
        # Generate comparison summary
        comparison_summary = {
            "total_evaluated": len(evaluations),
            "average_score": sum(e.overall_score for e in evaluations) / len(evaluations) if evaluations else 0,
            "best_score": best_supplier.overall_score if best_supplier else 0
        }
        
        return ComparisonResponse(
            product_id=request.product_id,
            evaluations=evaluations,
            best_supplier=best_supplier,
            comparison_summary=comparison_summary
        )
    
    def get_best_offers(self, product_id: str, limit: int = 10) -> BestOffersResponse:
        """Get best offers for a product."""
        # Check cache first
        cached = self.cache.get_best_offers(product_id)
        if cached:
            return BestOffersResponse(
                product_id=product_id,
                offers=[SupplierEvaluationResponse(**o) for o in cached],
                count=len(cached)
            )
        
        # Get from repository
        evaluations = self.repository.get_best_evaluations(product_id, limit)
        offers = [SupplierEvaluationResponse.from_orm(e) for e in evaluations]
        
        # Cache the result
        self.cache.set_best_offers(product_id, [o.dict() for o in offers])
        
        return BestOffersResponse(
            product_id=product_id,
            offers=offers,
            count=len(offers)
        )
