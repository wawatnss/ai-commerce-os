"""
Background Tasks for Product Intelligence

This module implements async background tasks for product analysis.
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..engines import ProductScoreEngine
from ..repositories.product_repository import ProductRepository
from ..cache.product_cache import ProductCache
from app.trend_intelligence.repositories.trend_repository import TrendRepository
from app.trend_intelligence.schemas.trend import TrendFilterParams


class AnalysisTask:
    """
    Background task for product analysis.
    
    Executes product analysis asynchronously without blocking the API.
    """
    
    def __init__(
        self,
        product_repository: ProductRepository,
        trend_repository: TrendRepository,
        cache: ProductCache,
        score_engine: Optional[ProductScoreEngine] = None
    ):
        """
        Initialize the analysis task.
        
        Args:
            product_repository: Product repository
            trend_repository: Trend repository
            cache: Redis cache
            score_engine: Optional scoring engine
        """
        self.product_repository = product_repository
        self.trend_repository = trend_repository
        self.cache = cache
        self.score_engine = score_engine or ProductScoreEngine()
    
    async def execute_analysis(
        self,
        trend_id: str,
        force_reanalyze: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a product analysis task.
        
        Args:
            trend_id: Trend ID to analyze
            force_reanalyze: Force reanalysis even if recent report exists
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Check cache first
            if not force_reanalyze:
                cached = self.cache.get_report(trend_id)
                if cached:
                    return {
                        "success": True,
                        "cached": True,
                        "trend_id": trend_id,
                        "report": cached
                    }
            
            # Get trend data
            trend = self.trend_repository.get_trend_by_trend_id(trend_id)
            if not trend:
                return {
                    "success": False,
                    "error": f"Trend {trend_id} not found",
                    "trend_id": trend_id
                }
            
            # Prepare trend data for analysis
            trend_data = {
                "product_name": trend.product_name,
                "category": trend.category,
                "popularity_score": trend.popularity_score,
                "growth_score": trend.growth_score,
                "competition_score": trend.competition_score,
                "opportunity_score": trend.opportunity_score,
                "confidence_score": trend.confidence_score,
                "detected_at": trend.detected_at
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
            existing_report = self.product_repository.get_report_by_trend_id(trend_id)
            if existing_report:
                self.product_repository.update_report(existing_report.id, report_data)
                report = self.product_repository.get_report_by_id(existing_report.id)
            else:
                report = self.product_repository.create_report(report_data)
            
            # Cache the result
            self.cache.set_report(trend_id, report.to_dict())
            
            return {
                "success": True,
                "cached": False,
                "trend_id": trend_id,
                "report": report.to_dict(),
                "overall_score": score_result.overall_score,
                "recommendation": score_result.recommendation.value
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "trend_id": trend_id
            }
    
    async def execute_batch_analysis(
        self,
        trend_ids: Optional[List[str]] = None,
        category: Optional[str] = None,
        min_overall_score: Optional[float] = None,
        analyze_all: bool = False,
        force_reanalyze: bool = False
    ) -> Dict[str, Any]:
        """
        Execute batch product analysis.
        
        Args:
            trend_ids: Specific trend IDs to analyze
            category: Analyze all trends in category
            min_overall_score: Minimum trend score
            analyze_all: Analyze all active trends
            force_reanalyze: Force reanalysis
            
        Returns:
            Dictionary with batch analysis results
        """
        job_id = str(uuid.uuid4())
        analyzed = 0
        failed = 0
        
        try:
            # Get trends to analyze
            if trend_ids:
                trends = [
                    self.trend_repository.get_trend_by_trend_id(tid)
                    for tid in trend_ids
                ]
                trends = [t for t in trends if t is not None]
            else:
                filters = TrendFilterParams(
                    category=category,
                    min_overall_score=min_overall_score
                )
                trends, _ = self.trend_repository.get_trends(
                    skip=0,
                    limit=1000 if analyze_all else 100,
                    filters=filters
                )
            
            # Analyze each trend
            for trend in trends:
                try:
                    result = await self.execute_analysis(trend.trend_id, force_reanalyze)
                    if result.get("success"):
                        analyzed += 1
                    else:
                        failed += 1
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
