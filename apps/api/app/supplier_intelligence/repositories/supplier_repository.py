"""
Repository for Supplier Intelligence Database Operations

This module handles all database operations for suppliers, offers, and evaluations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from ..models.supplier import Supplier, SupplierOffer, SupplierEvaluation
from ..schemas.supplier import SupplierCreate, SupplierOfferCreate, SupplierFilterParams, EvaluationFilterParams, Recommendation


class SupplierRepository:
    """
    Repository for supplier database operations.
    """
    
    def __init__(self, db: Session):
        """Initialize the repository."""
        self.db = db
    
    # Supplier Operations
    
    def create_supplier(self, supplier_data: Dict[str, Any]) -> Supplier:
        """Create a new supplier."""
        db_supplier = Supplier(
            supplier_id=supplier_data["supplier_id"],
            name=supplier_data["name"],
            source=supplier_data["source"],
            country=supplier_data.get("country"),
            currency=supplier_data.get("currency"),
            contact=supplier_data.get("contact"),
            metadata=supplier_data.get("metadata", {})
        )
        
        self.db.add(db_supplier)
        self.db.commit()
        self.db.refresh(db_supplier)
        
        return db_supplier
    
    def get_supplier_by_id(self, supplier_id: str) -> Optional[Supplier]:
        """Get a supplier by external ID."""
        return self.db.query(Supplier).filter(
            Supplier.supplier_id == supplier_id
        ).first()
    
    def get_suppliers(self, filters: Optional[SupplierFilterParams] = None) -> List[Supplier]:
        """Get suppliers with optional filtering."""
        query = self.db.query(Supplier)
        
        if filters:
            if filters.source:
                query = query.filter(Supplier.source == filters.source)
            if filters.country:
                query = query.filter(Supplier.country == filters.country)
            if filters.created_after:
                query = query.filter(Supplier.created_at >= filters.created_after)
        
        return query.order_by(desc(Supplier.created_at)).all()
    
    # Offer Operations
    
    def create_offer(self, offer_data: Dict[str, Any]) -> SupplierOffer:
        """Create a new supplier offer."""
        db_offer = SupplierOffer(
            supplier_id=offer_data["supplier_id"],
            product_id=offer_data["product_id"],
            unit_cost=offer_data["unit_cost"],
            minimum_order_quantity=offer_data["minimum_order_quantity"],
            estimated_processing_time=offer_data["estimated_processing_time"],
            estimated_shipping_time=offer_data["estimated_shipping_time"],
            available_quantity=offer_data.get("available_quantity"),
            currency=offer_data.get("currency"),
            metadata=offer_data.get("metadata", {})
        )
        
        self.db.add(db_offer)
        self.db.commit()
        self.db.refresh(db_offer)
        
        return db_offer
    
    def get_offers_by_product(self, product_id: str) -> List[SupplierOffer]:
        """Get all offers for a product."""
        return self.db.query(SupplierOffer).filter(
            SupplierOffer.product_id == product_id
        ).order_by(desc(SupplierOffer.last_updated)).all()
    
    def get_offers_by_supplier(self, supplier_id: str) -> List[SupplierOffer]:
        """Get all offers from a supplier."""
        return self.db.query(SupplierOffer).filter(
            SupplierOffer.supplier_id == supplier_id
        ).all()
    
    # Evaluation Operations
    
    def create_evaluation(self, evaluation_data: Dict[str, Any]) -> SupplierEvaluation:
        """Create a new supplier evaluation."""
        db_evaluation = SupplierEvaluation(
            supplier_id=evaluation_data["supplier_id"],
            product_id=evaluation_data["product_id"],
            cost_score=evaluation_data.get("cost_score", 0),
            delivery_score=evaluation_data.get("delivery_score", 0),
            moq_score=evaluation_data.get("moq_score", 0),
            availability_score=evaluation_data.get("availability_score", 0),
            reliability_score=evaluation_data.get("reliability_score", 0),
            flexibility_score=evaluation_data.get("flexibility_score", 0),
            data_quality_score=evaluation_data.get("data_quality_score", 0),
            overall_score=evaluation_data.get("overall_score", 0),
            confidence_score=evaluation_data.get("confidence_score", 0),
            recommendation=evaluation_data.get("recommendation", "consider"),
            reasoning=evaluation_data.get("reasoning", ""),
            strengths=evaluation_data.get("strengths", []),
            weaknesses=evaluation_data.get("weaknesses", []),
            rule_results=evaluation_data.get("rule_results", {}),
            rule_config=evaluation_data.get("rule_config", {})
        )
        
        self.db.add(db_evaluation)
        self.db.commit()
        self.db.refresh(db_evaluation)
        
        return db_evaluation
    
    def get_evaluation(self, supplier_id: str, product_id: str) -> Optional[SupplierEvaluation]:
        """Get an evaluation for a supplier-product pair."""
        return self.db.query(SupplierEvaluation).filter(
            and_(
                SupplierEvaluation.supplier_id == supplier_id,
                SupplierEvaluation.product_id == product_id
            )
        ).first()
    
    def get_evaluations(self, filters: Optional[EvaluationFilterParams] = None) -> List[SupplierEvaluation]:
        """Get evaluations with optional filtering."""
        query = self.db.query(SupplierEvaluation)
        
        if filters:
            if filters.product_id:
                query = query.filter(SupplierEvaluation.product_id == filters.product_id)
            if filters.min_overall_score is not None:
                query = query.filter(SupplierEvaluation.overall_score >= filters.min_overall_score)
            if filters.recommendation:
                query = query.filter(SupplierEvaluation.recommendation == filters.recommendation.value)
            if filters.created_after:
                query = query.filter(SupplierEvaluation.created_at >= filters.created_after)
        
        return query.order_by(desc(SupplierEvaluation.overall_score)).all()
    
    def get_best_evaluations(self, product_id: str, limit: int = 10) -> List[SupplierEvaluation]:
        """Get top evaluations for a product."""
        return self.db.query(SupplierEvaluation).filter(
            SupplierEvaluation.product_id == product_id
        ).order_by(desc(SupplierEvaluation.overall_score)).limit(limit).all()
