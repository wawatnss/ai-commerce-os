"""
Repository for Trend Database Operations

This module handles all database operations for trend data.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from ..models.trend import Trend, TrendCollection, TrendScoreHistory
from ..schemas.trend import TrendItemCreate, TrendItemUpdate, CollectionStatus, TrendFilterParams


class TrendRepository:
    """
    Repository for trend database operations.
    
    Provides methods for CRUD operations and complex queries on trend data.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the repository.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create_trend(self, trend_data: TrendItemCreate) -> Trend:
        """
        Create a new trend item.
        
        Args:
            trend_data: Trend item data
            
        Returns:
            Created trend model
        """
        db_trend = Trend(
            trend_id=trend_data.trend_id,
            source=trend_data.source,
            product_name=trend_data.product_name,
            brand=trend_data.brand,
            category=trend_data.category,
            tags=trend_data.tags,
            popularity_score=trend_data.popularity_score,
            growth_score=trend_data.growth_score,
            competition_score=trend_data.competition_score,
            opportunity_score=trend_data.opportunity_score,
            confidence_score=trend_data.confidence_score,
            detected_at=trend_data.detected_at,
            metadata=trend_data.metadata,
            collected_at=datetime.utcnow()
        )
        
        self.db.add(db_trend)
        self.db.commit()
        self.db.refresh(db_trend)
        
        return db_trend
    
    def get_trend_by_id(self, trend_id: int) -> Optional[Trend]:
        """
        Get a trend by database ID.
        
        Args:
            trend_id: Database ID
            
        Returns:
            Trend model or None
        """
        return self.db.query(Trend).filter(Trend.id == trend_id).first()
    
    def get_trend_by_trend_id(self, trend_id: str) -> Optional[Trend]:
        """
        Get a trend by trend identifier.
        
        Args:
            trend_id: Trend identifier
            
        Returns:
            Trend model or None
        """
        return self.db.query(Trend).filter(Trend.trend_id == trend_id).first()
    
    def get_trends(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[TrendFilterParams] = None,
        sort_by: str = "overall_score",
        sort_order: str = "desc"
    ) -> tuple[List[Trend], int]:
        """
        Get trends with optional filtering and pagination.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            filters: Optional filter parameters
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            Tuple of (trends list, total count)
        """
        query = self.db.query(Trend)
        
        # Apply filters
        if filters:
            if filters.source:
                query = query.filter(Trend.source == filters.source)
            
            if filters.category:
                query = query.filter(Trend.category == filters.category)
            
            if filters.brand:
                query = query.filter(Trend.brand == filters.brand)
            
            if filters.min_overall_score is not None:
                query = query.filter(Trend.overall_score >= filters.min_overall_score)
            
            if filters.max_overall_score is not None:
                query = query.filter(Trend.overall_score <= filters.max_overall_score)
            
            if filters.min_growth_score is not None:
                query = query.filter(Trend.growth_score >= filters.min_growth_score)
            
            if filters.min_opportunity_score is not None:
                query = query.filter(Trend.opportunity_score >= filters.min_opportunity_score)
            
            if filters.max_competition_score is not None:
                query = query.filter(Trend.competition_score <= filters.max_competition_score)
            
            if filters.is_active is not None:
                query = query.filter(Trend.is_active == filters.is_active)
            
            if filters.is_processed is not None:
                query = query.filter(Trend.is_processed == filters.is_processed)
            
            if filters.tags:
                # Filter for trends that contain any of the specified tags
                for tag in filters.tags:
                    query = query.filter(Trend.tags.contains([tag]))
            
            if filters.detected_after:
                query = query.filter(Trend.detected_at >= filters.detected_after)
            
            if filters.detected_before:
                query = query.filter(Trend.detected_at <= filters.detected_before)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(Trend, sort_by, Trend.overall_score)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        trends = query.offset(skip).limit(limit).all()
        
        return trends, total
    
    def update_trend(self, trend_id: int, update_data: TrendItemUpdate) -> Optional[Trend]:
        """
        Update a trend item.
        
        Args:
            trend_id: Database ID
            update_data: Update data
            
        Returns:
            Updated trend model or None
        """
        db_trend = self.get_trend_by_id(trend_id)
        if not db_trend:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_trend, field, value)
        
        db_trend.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_trend)
        
        return db_trend
    
    def delete_trend(self, trend_id: int) -> bool:
        """
        Delete a trend item.
        
        Args:
            trend_id: Database ID
            
        Returns:
            True if deleted, False otherwise
        """
        db_trend = self.get_trend_by_id(trend_id)
        if not db_trend:
            return False
        
        self.db.delete(db_trend)
        self.db.commit()
        
        return True
    
    def bulk_create_trends(self, trend_items: List[TrendItemCreate]) -> List[Trend]:
        """
        Create multiple trend items in bulk.
        
        Args:
            trend_items: List of trend item data
            
        Returns:
            List of created trend models
        """
        db_trends = []
        for item in trend_items:
            db_trend = Trend(
                trend_id=item.trend_id,
                source=item.source,
                product_name=item.product_name,
                brand=item.brand,
                category=item.category,
                tags=item.tags,
                popularity_score=item.popularity_score,
                growth_score=item.growth_score,
                competition_score=item.competition_score,
                opportunity_score=item.opportunity_score,
                confidence_score=item.confidence_score,
                detected_at=item.detected_at,
                metadata=item.metadata,
                collected_at=datetime.utcnow()
            )
            db_trends.append(db_trend)
        
        self.db.add_all(db_trends)
        self.db.commit()
        
        for trend in db_trends:
            self.db.refresh(trend)
        
        return db_trends
    
    def update_trend_score(
        self,
        trend_id: int,
        overall_score: float,
        component_scores: Dict[str, float],
        weighted_scores: Dict[str, float]
    ) -> Optional[Trend]:
        """
        Update trend scores.
        
        Args:
            trend_id: Database ID
            overall_score: Overall score
            component_scores: Component score breakdown
            weighted_scores: Weighted component scores
            
        Returns:
            Updated trend model or None
        """
        db_trend = self.get_trend_by_id(trend_id)
        if not db_trend:
            return None
        
        db_trend.overall_score = overall_score
        db_trend.component_scores = component_scores
        db_trend.weighted_scores = weighted_scores
        db_trend.scored_at = datetime.utcnow()
        db_trend.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_trend)
        
        return db_trend
    
    def create_collection(
        self,
        collection_id: str,
        provider: str,
        parameters: Dict[str, Any]
    ) -> TrendCollection:
        """
        Create a collection job record.
        
        Args:
            collection_id: Collection identifier
            provider: Provider name
            parameters: Collection parameters
            
        Returns:
            Created collection model
        """
        collection = TrendCollection(
            collection_id=collection_id,
            provider=provider,
            parameters=parameters,
            status=CollectionStatus.PENDING
        )
        
        self.db.add(collection)
        self.db.commit()
        self.db.refresh(collection)
        
        return collection
    
    def update_collection(
        self,
        collection_id: str,
        status: CollectionStatus,
        items_collected: int = 0,
        items_processed: int = 0,
        items_failed: int = 0,
        error_message: Optional[str] = None
    ) -> Optional[TrendCollection]:
        """
        Update a collection job.
        
        Args:
            collection_id: Collection identifier
            status: New status
            items_collected: Number of items collected
            items_processed: Number of items processed
            items_failed: Number of items failed
            error_message: Error message if failed
            
        Returns:
            Updated collection model or None
        """
        collection = self.db.query(TrendCollection).filter(
            TrendCollection.collection_id == collection_id
        ).first()
        
        if not collection:
            return None
        
        collection.status = status
        collection.items_collected = items_collected
        collection.items_processed = items_processed
        collection.items_failed = items_failed
        collection.error_message = error_message
        
        if status == CollectionStatus.RUNNING and not collection.started_at:
            collection.started_at = datetime.utcnow()
        
        if status in [CollectionStatus.COMPLETED, CollectionStatus.FAILED, CollectionStatus.CANCELLED]:
            collection.completed_at = datetime.utcnow()
            if collection.started_at:
                collection.duration_seconds = (
                    collection.completed_at - collection.started_at
                ).total_seconds()
        
        collection.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(collection)
        
        return collection
    
    def get_collection(self, collection_id: str) -> Optional[TrendCollection]:
        """
        Get a collection by ID.
        
        Args:
            collection_id: Collection identifier
            
        Returns:
            Collection model or None
        """
        return self.db.query(TrendCollection).filter(
            TrendCollection.collection_id == collection_id
        ).first()
    
    def get_recent_collections(
        self,
        provider: Optional[str] = None,
        limit: int = 10
    ) -> List[TrendCollection]:
        """
        Get recent collection jobs.
        
        Args:
            provider: Optional provider filter
            limit: Maximum number to return
            
        Returns:
            List of collection models
        """
        query = self.db.query(TrendCollection)
        
        if provider:
            query = query.filter(TrendCollection.provider == provider)
        
        return query.order_by(desc(TrendCollection.created_at)).limit(limit).all()
    
    def save_score_history(
        self,
        trend_id: str,
        scores: Dict[str, float],
        component_scores: Dict[str, float],
        weighted_scores: Dict[str, float],
        score_weights: Dict[str, float]
    ) -> TrendScoreHistory:
        """
        Save score history for a trend.
        
        Args:
            trend_id: Trend identifier
            scores: Individual scores
            component_scores: Component score breakdown
            weighted_scores: Weighted component scores
            score_weights: Weights used for calculation
            
        Returns:
            Created score history model
        """
        history = TrendScoreHistory(
            trend_id=trend_id,
            popularity_score=scores.get("popularity", 0),
            growth_score=scores.get("growth", 0),
            competition_score=scores.get("competition", 0),
            opportunity_score=scores.get("opportunity", 0),
            confidence_score=scores.get("confidence", 0),
            overall_score=scores.get("overall", 0),
            component_scores=component_scores,
            weighted_scores=weighted_scores,
            score_weights=score_weights
        )
        
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        
        return history
    
    def get_trend_analytics(self) -> Dict[str, Any]:
        """
        Get trend analytics.
        
        Returns:
            Dictionary with analytics data
        """
        total_trends = self.db.query(func.count(Trend.id)).scalar()
        active_trends = self.db.query(func.count(Trend.id)).filter(
            Trend.is_active == True
        ).scalar()
        
        avg_score = self.db.query(func.avg(Trend.overall_score)).scalar() or 0
        
        # Top categories
        top_categories = self.db.query(
            Trend.category,
            func.count(Trend.id).label('count')
        ).group_by(Trend.category).order_by(
            desc('count')
        ).limit(10).all()
        
        # Top sources
        top_sources = self.db.query(
            Trend.source,
            func.count(Trend.id).label('count')
        ).group_by(Trend.source).order_by(
            desc('count')
        ).limit(10).all()
        
        # Score distribution
        score_ranges = [
            (0, 20), (20, 40), (40, 60), (60, 80), (80, 100)
        ]
        score_distribution = {}
        for min_score, max_score in score_ranges:
            count = self.db.query(func.count(Trend.id)).filter(
                and_(
                    Trend.overall_score >= min_score,
                    Trend.overall_score < max_score
                )
            ).scalar()
            score_distribution[f"{min_score}-{max_score}"] = count or 0
        
        # Recent trends (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_trends = self.db.query(func.count(Trend.id)).filter(
            Trend.detected_at >= week_ago
        ).scalar()
        
        # High growth trends (growth score > 70)
        growth_trends = self.db.query(func.count(Trend.id)).filter(
            Trend.growth_score > 70
        ).scalar()
        
        return {
            "total_trends": total_trends or 0,
            "active_trends": active_trends or 0,
            "average_overall_score": round(avg_score, 2),
            "top_categories": [
                {"category": cat, "count": count}
                for cat, count in top_categories
            ],
            "top_sources": [
                {"source": source, "count": count}
                for source, count in top_sources
            ],
            "score_distribution": score_distribution,
            "recent_trends": recent_trends or 0,
            "growth_trends": growth_trends or 0
        }
    
    def cleanup_old_trends(self, days: int = 30) -> int:
        """
        Delete inactive trends older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of trends deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted = self.db.query(Trend).filter(
            and_(
                Trend.is_active == False,
                Trend.detected_at < cutoff_date
            )
        ).delete()
        
        self.db.commit()
        
        return deleted
