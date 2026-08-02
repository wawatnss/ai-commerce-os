"""
Repository for Product Intelligence Database Operations

This module handles all database operations for product intelligence reports.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from ..models.product import ProductIntelligenceReport
from ..schemas.product import ProductIntelligenceReportCreate, ProductIntelligenceReportUpdate, ProductFilterParams, Recommendation


class ProductRepository:
    """
    Repository for product intelligence database operations.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the repository.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create_report(self, report_data: Dict[str, Any]) -> ProductIntelligenceReport:
        """
        Create a new product intelligence report.
        
        Args:
            report_data: Report data dictionary
            
        Returns:
            Created report model
        """
        db_report = ProductIntelligenceReport(
            trend_id=report_data["trend_id"],
            product_name=report_data["product_name"],
            category=report_data["category"],
            estimated_margin_score=report_data.get("estimated_margin_score", 0),
            demand_score=report_data.get("demand_score", 0),
            competition_score=report_data.get("competition_score", 0),
            shipping_complexity_score=report_data.get("shipping_complexity_score", 0),
            supplier_availability_score=report_data.get("supplier_availability_score", 0),
            seasonality_score=report_data.get("seasonality_score", 0),
            impulse_buy_score=report_data.get("impulse_buy_score", 0),
            content_potential_score=report_data.get("content_potential_score", 0),
            seo_potential_score=report_data.get("seo_potential_score", 0),
            return_risk_score=report_data.get("return_risk_score", 0),
            legal_risk_score=report_data.get("legal_risk_score", 0),
            overall_score=report_data.get("overall_score", 0),
            confidence_score=report_data.get("confidence_score", 0),
            recommendation=report_data.get("recommendation", "hold"),
            reasoning=report_data.get("reasoning", ""),
            strengths=report_data.get("strengths", []),
            weaknesses=report_data.get("weaknesses", []),
            rule_results=report_data.get("rule_results", {}),
            trend_data=report_data.get("trend_data", {}),
            analyzed_at=datetime.utcnow()
        )
        
        self.db.add(db_report)
        self.db.commit()
        self.db.refresh(db_report)
        
        return db_report
    
    def get_report_by_id(self, report_id: int) -> Optional[ProductIntelligenceReport]:
        """
        Get a report by database ID.
        
        Args:
            report_id: Database ID
            
        Returns:
            Report model or None
        """
        return self.db.query(ProductIntelligenceReport).filter(
            ProductIntelligenceReport.id == report_id
        ).first()
    
    def get_report_by_trend_id(self, trend_id: str) -> Optional[ProductIntelligenceReport]:
        """
        Get a report by trend ID.
        
        Args:
            trend_id: Trend identifier
            
        Returns:
            Report model or None
        """
        return self.db.query(ProductIntelligenceReport).filter(
            ProductIntelligenceReport.trend_id == trend_id
        ).first()
    
    def get_reports(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[ProductFilterParams] = None,
        sort_by: str = "overall_score",
        sort_order: str = "desc"
    ) -> tuple[List[ProductIntelligenceReport], int]:
        """
        Get reports with optional filtering and pagination.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            filters: Optional filter parameters
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            Tuple of (reports list, total count)
        """
        query = self.db.query(ProductIntelligenceReport)
        
        # Apply filters
        if filters:
            if filters.category:
                query = query.filter(ProductIntelligenceReport.category == filters.category)
            
            if filters.min_overall_score is not None:
                query = query.filter(ProductIntelligenceReport.overall_score >= filters.min_overall_score)
            
            if filters.max_overall_score is not None:
                query = query.filter(ProductIntelligenceReport.overall_score <= filters.max_overall_score)
            
            if filters.recommendation:
                query = query.filter(ProductIntelligenceReport.recommendation == filters.recommendation.value)
            
            if filters.min_confidence_score is not None:
                query = query.filter(ProductIntelligenceReport.confidence_score >= filters.min_confidence_score)
            
            if filters.created_after:
                query = query.filter(ProductIntelligenceReport.created_at >= filters.created_after)
            
            if filters.created_before:
                query = query.filter(ProductIntelligenceReport.created_at <= filters.created_before)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(ProductIntelligenceReport, sort_by, ProductIntelligenceReport.overall_score)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        reports = query.offset(skip).limit(limit).all()
        
        return reports, total
    
    def update_report(self, report_id: int, update_data: Dict[str, Any]) -> Optional[ProductIntelligenceReport]:
        """
        Update a report.
        
        Args:
            report_id: Database ID
            update_data: Update data
            
        Returns:
            Updated report model or None
        """
        db_report = self.get_report_by_id(report_id)
        if not db_report:
            return None
        
        for field, value in update_data.items():
            if hasattr(db_report, field):
                setattr(db_report, field, value)
        
        db_report.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_report)
        
        return db_report
    
    def delete_report(self, report_id: int) -> bool:
        """
        Delete a report.
        
        Args:
            report_id: Database ID
            
        Returns:
            True if deleted, False otherwise
        """
        db_report = self.get_report_by_id(report_id)
        if not db_report:
            return False
        
        self.db.delete(db_report)
        self.db.commit()
        
        return True
    
    def get_top_products(self, limit: int = 100, min_score: float = 60) -> List[ProductIntelligenceReport]:
        """
        Get top products by overall score.
        
        Args:
            limit: Maximum number to return
            min_score: Minimum overall score
            
        Returns:
            List of report models
        """
        return self.db.query(ProductIntelligenceReport).filter(
            ProductIntelligenceReport.overall_score >= min_score
        ).order_by(
            desc(ProductIntelligenceReport.overall_score)
        ).limit(limit).all()
    
    def get_top_products_by_category(self, category: str, limit: int = 10) -> List[ProductIntelligenceReport]:
        """
        Get top products in a specific category.
        
        Args:
            category: Product category
            limit: Maximum number to return
            
        Returns:
            List of report models
        """
        return self.db.query(ProductIntelligenceReport).filter(
            ProductIntelligenceReport.category == category
        ).order_by(
            desc(ProductIntelligenceReport.overall_score)
        ).limit(limit).all()
    
    def get_analytics(self) -> Dict[str, Any]:
        """
        Get product intelligence analytics.
        
        Returns:
            Dictionary with analytics data
        """
        total_reports = self.db.query(func.count(ProductIntelligenceReport.id)).scalar()
        
        avg_overall_score = self.db.query(func.avg(ProductIntelligenceReport.overall_score)).scalar() or 0
        avg_confidence_score = self.db.query(func.avg(ProductIntelligenceReport.confidence_score)).scalar() or 0
        
        # Recommendation distribution
        recommendation_distribution = {}
        for rec in ["strong_buy", "buy", "hold", "avoid"]:
            count = self.db.query(func.count(ProductIntelligenceReport.id)).filter(
                ProductIntelligenceReport.recommendation == rec
            ).scalar()
            recommendation_distribution[rec] = count or 0
        
        # Top categories
        top_categories = self.db.query(
            ProductIntelligenceReport.category,
            func.count(ProductIntelligenceReport.id).label('count'),
            func.avg(ProductIntelligenceReport.overall_score).label('avg_score')
        ).group_by(ProductIntelligenceReport.category).order_by(
            desc('count')
        ).limit(10).all()
        
        # Score distribution
        score_ranges = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 100)]
        score_distribution = {}
        for min_score, max_score in score_ranges:
            count = self.db.query(func.count(ProductIntelligenceReport.id)).filter(
                and_(
                    ProductIntelligenceReport.overall_score >= min_score,
                    ProductIntelligenceReport.overall_score < max_score
                )
            ).scalar()
            score_distribution[f"{min_score}-{max_score}"] = count or 0
        
        # Recent analyses (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_analyses = self.db.query(func.count(ProductIntelligenceReport.id)).filter(
            ProductIntelligenceReport.created_at >= week_ago
        ).scalar()
        
        # High opportunity products (score > 70)
        high_opportunity = self.db.query(func.count(ProductIntelligenceReport.id)).filter(
            ProductIntelligenceReport.overall_score > 70
        ).scalar()
        
        return {
            "total_reports": total_reports or 0,
            "average_overall_score": round(avg_overall_score, 2),
            "average_confidence_score": round(avg_confidence_score, 2),
            "recommendation_distribution": recommendation_distribution,
            "top_categories": [
                {"category": cat, "count": count, "avg_score": round(avg_score, 2)}
                for cat, count, avg_score in top_categories
            ],
            "score_distribution": score_distribution,
            "recent_analyses": recent_analyses or 0,
            "high_opportunity_products": high_opportunity or 0
        }
    
    def cleanup_old_reports(self, days: int = 30) -> int:
        """
        Delete reports older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of reports deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted = self.db.query(ProductIntelligenceReport).filter(
            ProductIntelligenceReport.created_at < cutoff_date
        ).delete()
        
        self.db.commit()
        
        return deleted
