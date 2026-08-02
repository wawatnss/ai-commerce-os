"""
Trend Intelligence Service

This module provides the main service layer for trend intelligence operations,
coordinating between providers, scoring, caching, and repository operations.
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from ..providers import get_registry, TrendItem
from ..scoring import ScoreEngine, ScoreWeights
from ..repositories.trend_repository import TrendRepository
from ..cache import TrendCache
from ..schemas.trend import (
    TrendItemCreate,
    TrendItemUpdate,
    TrendItemResponse,
    TrendListResponse,
    CollectionRequest,
    CollectionResponse,
    ScoreRecalculateRequest,
    ScoreRecalculateResponse,
    TrendFilterParams,
    TrendAnalyticsResponse,
    ProviderInfo,
    ProviderListResponse,
    CollectionStatus
)
from ..tasks.collection_task import CollectionTask


class TrendService:
    """
    Main service for trend intelligence operations.
    
    Provides high-level methods for trend collection, scoring, and retrieval.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the trend service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.repository = TrendRepository(db)
        self.cache = TrendCache()
        self.score_engine = ScoreEngine()
        self.collection_task = CollectionTask(
            self.repository,
            self.cache,
            self.score_engine
        )
        self.registry = get_registry()
    
    # Trend CRUD Operations
    
    def get_trend(self, trend_id: int) -> Optional[TrendItemResponse]:
        """
        Get a trend by ID.
        
        Args:
            trend_id: Database ID
            
        Returns:
            Trend response or None
        """
        # Try cache first
        cached = self.cache.get_trend(str(trend_id))
        if cached:
            return TrendItemResponse(**cached)
        
        # Get from database
        trend = self.repository.get_trend_by_id(trend_id)
        if not trend:
            return None
        
        response = TrendItemResponse.from_orm(trend)
        
        # Cache the result
        self.cache.set_trend(str(trend_id), response.dict())
        
        return response
    
    def get_trends(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[TrendFilterParams] = None,
        sort_by: str = "overall_score",
        sort_order: str = "desc"
    ) -> TrendListResponse:
        """
        Get trends with pagination and filtering.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            filters: Optional filter parameters
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            Paginated trend list response
        """
        # Generate cache key
        cache_key = f"trends:list:{page}:{page_size}:{sort_by}:{sort_order}"
        if filters:
            filter_str = str(filters.dict(exclude_none=True))
            cache_key += f":{hash(filter_str)}"
        
        # Try cache first
        cached = self.cache.get_trends_list(cache_key)
        if cached:
            return TrendListResponse(**cached)
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get from database
        trends, total = self.repository.get_trends(
            skip=skip,
            limit=page_size,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Convert to response models
        items = [TrendItemResponse.from_orm(trend) for trend in trends]
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        response = TrendListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
        # Cache the result
        self.cache.set_trends_list(cache_key, response.dict(), ttl=300)  # 5 minutes
        
        return response
    
    def create_trend(self, trend_data: TrendItemCreate) -> TrendItemResponse:
        """
        Create a new trend.
        
        Args:
            trend_data: Trend creation data
            
        Returns:
            Created trend response
        """
        # Create in database
        trend = self.repository.create_trend(trend_data)
        
        # Calculate scores
        score_data = trend_data.dict()
        score_result = self.score_engine.calculate_score(score_data)
        
        # Update with scores
        self.repository.update_trend_score(
            trend.id,
            score_result.overall_score,
            score_result.component_scores,
            score_result.weighted_scores
        )
        
        # Refresh from database
        trend = self.repository.get_trend_by_id(trend.id)
        
        response = TrendItemResponse.from_orm(trend)
        
        # Invalidate caches
        self.cache.invalidate_all_trends()
        
        return response
    
    def update_trend(self, trend_id: int, update_data: TrendItemUpdate) -> Optional[TrendItemResponse]:
        """
        Update a trend.
        
        Args:
            trend_id: Database ID
            update_data: Update data
            
        Returns:
            Updated trend response or None
        """
        trend = self.repository.update_trend(trend_id, update_data)
        if not trend:
            return None
        
        # Recalculate scores if score-related fields changed
        score_fields = [
            'popularity_score', 'growth_score', 'competition_score',
            'opportunity_score', 'confidence_score'
        ]
        if any(field in update_data.dict(exclude_unset=True) for field in score_fields):
            score_data = {
                "popularity_score": trend.popularity_score,
                "growth_score": trend.growth_score,
                "competition_score": trend.competition_score,
                "opportunity_score": trend.opportunity_score,
                "confidence_score": trend.confidence_score,
                "detected_at": trend.detected_at
            }
            score_result = self.score_engine.calculate_score(score_data)
            self.repository.update_trend_score(
                trend.id,
                score_result.overall_score,
                score_result.component_scores,
                score_result.weighted_scores
            )
            trend = self.repository.get_trend_by_id(trend_id)
        
        response = TrendItemResponse.from_orm(trend)
        
        # Invalidate caches
        self.cache.invalidate_trend(str(trend_id))
        
        return response
    
    def delete_trend(self, trend_id: int) -> bool:
        """
        Delete a trend.
        
        Args:
            trend_id: Database ID
            
        Returns:
            True if deleted
        """
        success = self.repository.delete_trend(trend_id)
        
        if success:
            self.cache.invalidate_trend(str(trend_id))
        
        return success
    
    # Collection Operations
    
    async def start_collection(self, request: CollectionRequest) -> CollectionResponse:
        """
        Start a trend collection task.
        
        Args:
            request: Collection request
            
        Returns:
            Collection response
        """
        # Validate provider
        if not self.registry.is_registered(request.provider):
            raise ValueError(f"Provider '{request.provider}' is not registered")
        
        # Generate collection ID
        collection_id = str(uuid.uuid4())
        
        # Create collection record
        parameters = {
            "category": request.category,
            "limit": request.limit,
            **request.parameters
        }
        
        self.repository.create_collection(
            collection_id,
            request.provider,
            parameters
        )
        
        # Execute collection task asynchronously
        # In production, this would be a proper background worker
        import asyncio
        asyncio.create_task(
            self.collection_task.execute_collection(
                request.provider,
                collection_id,
                parameters
            )
        )
        
        # Return initial response
        return CollectionResponse(
            collection_id=collection_id,
            provider=request.provider,
            status=CollectionStatus.PENDING,
            items_collected=0,
            items_processed=0,
            items_failed=0,
            started_at=None,
            completed_at=None,
            duration_seconds=None,
            error_message=None,
            created_at=datetime.utcnow()
        )
    
    def get_collection(self, collection_id: str) -> Optional[CollectionResponse]:
        """
        Get collection status.
        
        Args:
            collection_id: Collection identifier
            
        Returns:
            Collection response or None
        """
        # Try cache first
        cached = self.cache.get_collection_result(collection_id)
        if cached:
            return CollectionResponse(**cached)
        
        # Get from database
        collection = self.repository.get_collection(collection_id)
        if not collection:
            return None
        
        return CollectionResponse.from_orm(collection)
    
    def get_recent_collections(self, provider: Optional[str] = None, limit: int = 10) -> List[CollectionResponse]:
        """
        Get recent collections.
        
        Args:
            provider: Optional provider filter
            limit: Maximum number to return
            
        Returns:
            List of collection responses
        """
        collections = self.repository.get_recent_collections(provider, limit)
        return [CollectionResponse.from_orm(c) for c in collections]
    
    # Scoring Operations
    
    async def recalculate_scores(self, request: ScoreRecalculateRequest) -> ScoreRecalculateResponse:
        """
        Recalculate trend scores.
        
        Args:
            request: Score recalculation request
            
        Returns:
            Score recalculation response
        """
        # Execute recalculation task
        result = await self.collection_task.score_recalculation(
            trend_ids=request.trend_ids,
            category=request.category,
            min_overall_score=request.min_overall_score,
            recalculate_all=request.recalculate_all
        )
        
        return ScoreRecalculateResponse(
            job_id=result.get("job_id", ""),
            trends_queued=result.get("trends_processed", 0),
            status="completed" if result.get("success") else "failed",
            message=result.get("message", result.get("error", ""))
        )
    
    def update_score_weights(self, weights: ScoreWeights) -> bool:
        """
        Update scoring weights.
        
        Args:
            weights: New weight configuration
            
        Returns:
            True if successful
        """
        try:
            self.score_engine.update_weights(weights)
            return True
        except ValueError:
            return False
    
    # Analytics Operations
    
    def get_analytics(self) -> TrendAnalyticsResponse:
        """
        Get trend analytics.
        
        Returns:
            Analytics response
        """
        # Try cache first
        cached = self.cache.get_analytics()
        if cached:
            return TrendAnalyticsResponse(**cached)
        
        # Get from repository
        analytics = self.repository.get_trend_analytics()
        
        response = TrendAnalyticsResponse(**analytics)
        
        # Cache the result
        self.cache.set_analytics(analytics, ttl=300)  # 5 minutes
        
        return response
    
    # Provider Operations
    
    def get_providers(self) -> ProviderListResponse:
        """
        Get available providers.
        
        Returns:
            Provider list response
        """
        provider_names = self.registry.list_providers()
        
        providers = []
        for name in provider_names:
            last_collection = self.cache.get_provider_last_collection(name)
            collections = self.repository.get_recent_collections(name, limit=10)
            
            avg_items = None
            if collections:
                total_items = sum(c.items_collected for c in collections)
                avg_items = total_items / len(collections)
            
            providers.append(ProviderInfo(
                name=name,
                description=f"{name.replace('_', ' ').title()} provider",
                available=True,
                last_collection=datetime.fromisoformat(last_collection) if last_collection else None,
                total_collections=len(collections),
                average_items_per_collection=avg_items
            ))
        
        return ProviderListResponse(providers=providers)
    
    # Utility Operations
    
    def cleanup_old_trends(self, days: int = 30) -> int:
        """
        Clean up old inactive trends.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of trends deleted
        """
        deleted = self.repository.cleanup_old_trends(days)
        
        if deleted > 0:
            self.cache.invalidate_all_trends()
        
        return deleted
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Cache statistics
        """
        return self.cache.get_stats()
