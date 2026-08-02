"""
Product Intelligence Service

This module provides the main service layer for product intelligence operations.
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from ..engines import ProductScoreEngine, ScoreWeights
from ..repositories.product_repository import ProductRepository
from ..cache.product_cache import ProductCache
from ..schemas.product import (
    ProductIntelligenceReportResponse,
    ProductListResponse,
    ProductAnalysisRequest,
    BatchAnalysisRequest,
    ProductFilterParams,
    ProductAnalyticsResponse,
    TopProductsResponse,
    Recommendation
)
from app.trend_intelligence.repositories.trend_repository import TrendRepository


class ProductService:
    """
    Main service for product intelligence operations.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the product service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.repository = ProductRepository(db)
        self.trend_repository = TrendRepository(db)
        self.cache = ProductCache()
        self.score_engine = ProductScoreEngine()
    
    def analyze_product(self, trend_id: str, force_reanalyze: bool = False) -> ProductIntelligenceReportResponse:
        """
        Analyze a product based on trend data.
        
        Args:
            trend_id: Trend ID to analyze
            force_reanalyze: Force reanalysis even if recent report exists
            
        Returns:
            Product intelligence report response
        """
        # Check cache first
        if not force_reanalyze:
            cached = self.cache.get_report(trend_id)
            if cached:
                return ProductIntelligenceReportResponse(**cached)
        
        # Get trend data
        trend = self.trend_repository.get_trend_by_trend_id(trend_id)
        if not trend:
            raise ValueError(f"Trend {trend_id} not found")
        
        # Prepare trend data for analysis
        trend_data = {
            "product_name": trend.product_name,
            "category": trend.category,
            "popularity_score": trend.popularity_score,
            "growth_score": trend.growth_score,
            "competition_score": trend.competition_score,
            "opportunity_score": trend.opportunity_score,
            "confidence_score": trend.confidence_score,
            "detected_at": trend.detected_at.isoformat() if trend.detected_at else None
        }
        
        # Run analysis
        score_result = self.score_engine.analyze(trend_data)
        
        # Prepare report data
        report_data = {
            "trend_id": trend_id,
            "product_name": trend.product_name,
            "category": trend.category,
            "estimated_margin_score": score_result.rule_results.get("estimated_margin", {}).get("score", 0),
            "demand_score": score_result.rule_results.get("demand", {}).get("score", 0),
            "competition_score": score_result.rule_results.get("competition", {}).get("score", 0),
            "shipping_complexity_score": score_result.rule_results.get("shipping", {}).get("score", 0),
            "supplier_availability_score": score_result.rule_results.get("supplier_availability", {}).get("score", 0),
            "seasonality_score": score_result.rule_results.get("seasonality", {}).get("score", 0),
            "impulse_buy_score": score_result.rule_results.get("impulse_buy", {}).get("score", 0),
            "content_potential_score": score_result.rule_results.get("content_potential", {}).get("score", 0),
            "seo_potential_score": score_result.rule_results.get("seo", {}).get("score", 0),
            "return_risk_score": score_result.rule_results.get("return_risk", {}).get("score", 0),
            "legal_risk_score": score_result.rule_results.get("legal_risk", {}).get("score", 0),
            "overall_score": score_result.overall_score,
            "confidence_score": score_result.confidence_score,
            "recommendation": score_result.recommendation.value,
            "reasoning": score_result.reasoning,
            "strengths": score_result.strengths,
            "weaknesses": score_result.weaknesses,
            "rule_results": score_result.rule_results,
            "trend_data": trend_data
        }
        
        # Create or update report
        existing_report = self.repository.get_report_by_trend_id(trend_id)
        if existing_report:
            self.repository.update_report(existing_report.id, report_data)
            report = self.repository.get_report_by_id(existing_report.id)
        else:
            report = self.repository.create_report(report_data)
        
        # Cache the result
        self.cache.set_report(trend_id, report.to_dict())
        
        return ProductIntelligenceReportResponse.from_orm(report)
    
    def batch_analyze(self, request: BatchAnalysisRequest) -> Dict[str, Any]:
        """
        Analyze multiple products.
        
        Args:
            request: Batch analysis request
            
        Returns:
            Dictionary with batch analysis results
        """
        job_id = str(uuid.uuid4())
        analyzed = 0
        failed = 0
        
        try:
            # Get trends to analyze
            if request.trend_ids:
                trends = [
                    self.trend_repository.get_trend_by_trend_id(tid)
                    for tid in request.trend_ids
                ]
                trends = [t for t in trends if t is not None]
            else:
                from app.trend_intelligence.schemas.trend import TrendFilterParams
                filters = TrendFilterParams(
                    category=request.category,
                    min_overall_score=request.min_overall_score
                )
                trends, _ = self.trend_repository.get_trends(
                    skip=0,
                    limit=1000 if request.analyze_all else 100,
                    filters=filters
                )
            
            # Analyze each trend
            for trend in trends:
                try:
                    self.analyze_product(trend.trend_id, force_reanalyze=request.force_reanalyze)
                    analyzed += 1
                except Exception:
                    failed += 1
            
            # Invalidate caches
            self.cache.invalidate_all()
            
            return {
                "success": True,
                "job_id": job_id,
                "analyzed": analyzed,
                "failed": failed,
                "message": f"Analyzed {analyzed} products, {failed} failed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "job_id": job_id,
                "error": str(e),
                "analyzed": analyzed,
                "failed": failed
            }
    
    def get_reports(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[ProductFilterParams] = None,
        sort_by: str = "overall_score",
        sort_order: str = "desc"
    ) -> ProductListResponse:
        """Get reports with pagination and filtering."""
        skip = (page - 1) * page_size
        reports, total = self.repository.get_reports(
            skip=skip,
            limit=page_size,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        items = [ProductIntelligenceReportResponse.from_orm(r) for r in reports]
        total_pages = (total + page_size - 1) // page_size
        
        return ProductListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    def get_report(self, report_id: int) -> Optional[ProductIntelligenceReportResponse]:
        """Get a specific report by ID."""
        report = self.repository.get_report_by_id(report_id)
        if not report:
            return None
        return ProductIntelligenceReportResponse.from_orm(report)
    
    def get_top_products(self, limit: int = 100, min_score: float = 60) -> TopProductsResponse:
        """Get top products by overall score."""
        # Check cache first
        cached = self.cache.get_top_products(limit, min_score)
        if cached:
            return TopProductsResponse(
                products=[ProductIntelligenceReportResponse(**p) for p in cached],
                count=len(cached),
                criteria=f"score >= {min_score}"
            )
        
        # Get from repository
        reports = self.repository.get_top_products(limit, min_score)
        items = [ProductIntelligenceReportResponse.from_orm(r) for r in reports]
        
        # Cache the result
        self.cache.set_top_products(limit, min_score, [i.dict() for i in items])
        
        return TopProductsResponse(
            products=items,
            count=len(items),
            criteria=f"score >= {min_score}"
        )
    
    def get_analytics(self) -> ProductAnalyticsResponse:
        """Get product intelligence analytics."""
        # Check cache first
        cached = self.cache.get_analytics()
        if cached:
            return ProductAnalyticsResponse(**cached)
        
        # Get from repository
        analytics = self.repository.get_analytics()
        
        response = ProductAnalyticsResponse(**analytics)
        
        # Cache the result
        self.cache.set_analytics(analytics)
        
        return response
    
    def update_weights(self, weights: ScoreWeights) -> bool:
        """Update scoring weights."""
        try:
            self.score_engine.update_weights(weights)
            return True
        except ValueError:
            return False
