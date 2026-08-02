"""
Background Tasks for Trend Collection

This module implements async background tasks for trend data collection
using Redis as a task queue.
"""

import asyncio
import uuid
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..providers import get_registry, TrendItem
from ..scoring import ScoreEngine
from ..repositories.trend_repository import TrendRepository
from ..cache import TrendCache
from ..schemas.trend import CollectionStatus
from config import settings


class CollectionTask:
    """
    Background task for collecting trend data.
    
    Executes trend collection asynchronously without blocking the API.
    """
    
    def __init__(
        self,
        repository: TrendRepository,
        cache: TrendCache,
        score_engine: Optional[ScoreEngine] = None
    ):
        """
        Initialize the collection task.
        
        Args:
            repository: Trend repository
            cache: Redis cache
            score_engine: Optional scoring engine
        """
        self.repository = repository
        self.cache = cache
        self.score_engine = score_engine or ScoreEngine()
        self.registry = get_registry()
    
    async def execute_collection(
        self,
        provider_name: str,
        collection_id: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a trend collection task.
        
        Args:
            provider_name: Name of the provider to use
            collection_id: Collection identifier
            parameters: Collection parameters
            
        Returns:
            Dictionary with collection results
        """
        # Check if collection is already running
        if self.cache.check_collection_running(provider_name):
            return {
                "success": False,
                "error": "Collection already running for this provider",
                "collection_id": collection_id
            }
        
        # Mark as running
        self.cache.set_collection_running(provider_name, collection_id)
        
        try:
            # Update collection status to running
            self.repository.update_collection(
                collection_id,
                CollectionStatus.RUNNING
            )
            
            # Get provider instance
            provider = self.registry.get_provider(provider_name, parameters.get("config"))
            
            # Collect and normalize data
            trend_items = await provider.fetch_and_normalize(**parameters)
            
            # Update collection with counts
            items_collected = len(trend_items)
            items_processed = 0
            items_failed = 0
            
            # Process each trend item
            for item in trend_items:
                try:
                    # Calculate scores
                    score_result = self.score_engine.calculate_score(item.dict())
                    
                    # Check if trend already exists
                    existing_trend = self.repository.get_trend_by_trend_id(item.id)
                    
                    if existing_trend:
                        # Update existing trend
                        self.repository.update_trend(
                            existing_trend.id,
                            {
                                "popularity_score": item.popularity_score,
                                "growth_score": item.growth_score,
                                "competition_score": item.competition_score,
                                "opportunity_score": item.opportunity_score,
                                "confidence_score": item.confidence_score,
                                "overall_score": score_result.overall_score,
                                "component_scores": score_result.component_scores,
                                "weighted_scores": score_result.weighted_scores,
                                "scored_at": datetime.utcnow(),
                                "detected_at": item.detected_at
                            }
                        )
                    else:
                        # Create new trend
                        from ..schemas.trend import TrendItemCreate
                        trend_create = TrendItemCreate(
                            trend_id=item.id,
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
                            metadata=item.metadata
                        )
                        new_trend = self.repository.create_trend(trend_create)
                        
                        # Update with scores
                        self.repository.update_trend_score(
                            new_trend.id,
                            score_result.overall_score,
                            score_result.component_scores,
                            score_result.weighted_scores
                        )
                    
                    # Cache the trend
                    self.cache.set_trend(item.id, item.dict())
                    
                    items_processed += 1
                    
                except Exception as e:
                    items_failed += 1
                    # Log error in production
                    continue
            
            # Update collection status to completed
            self.repository.update_collection(
                collection_id,
                CollectionStatus.COMPLETED,
                items_collected=items_collected,
                items_processed=items_processed,
                items_failed=items_failed
            )
            
            # Cache the result
            result = {
                "success": True,
                "collection_id": collection_id,
                "provider": provider_name,
                "items_collected": items_collected,
                "items_processed": items_processed,
                "items_failed": items_failed,
                "completed_at": datetime.utcnow().isoformat()
            }
            self.cache.set_collection_result(collection_id, result)
            
            # Update provider's last collection
            self.cache.set_provider_last_collection(provider_name, collection_id)
            
            # Invalidate relevant caches
            self.cache.invalidate_all_trends()
            
            return result
            
        except Exception as e:
            # Update collection status to failed
            self.repository.update_collection(
                collection_id,
                CollectionStatus.FAILED,
                error_message=str(e)
            )
            
            return {
                "success": False,
                "error": str(e),
                "collection_id": collection_id
            }
            
        finally:
            # Clear running flag
            self.cache.clear_collection_running(provider_name)
    
    async def score_recalculation(
        self,
        trend_ids: Optional[List[str]] = None,
        category: Optional[str] = None,
        min_overall_score: Optional[float] = None,
        recalculate_all: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a score recalculation task.
        
        Args:
            trend_ids: Specific trend IDs to recalculate
            category: Recalculate all trends in category
            min_overall_score: Minimum overall score filter
            recalculate_all: Recalculate all active trends
            
        Returns:
            Dictionary with recalculation results
        """
        job_id = str(uuid.uuid4())
        trends_processed = 0
        trends_failed = 0
        
        try:
            # Get trends to recalculate
            if trend_ids:
                trends = [
                    self.repository.get_trend_by_trend_id(tid)
                    for tid in trend_ids
                ]
                trends = [t for t in trends if t is not None]
            else:
                from ..schemas.trend import TrendFilterParams
                filters = TrendFilterParams(
                    category=category,
                    min_overall_score=min_overall_score,
                    is_active=True
                )
                trends, _ = self.repository.get_trends(
                    skip=0,
                    limit=10000 if recalculate_all else 1000,
                    filters=filters
                )
            
            # Recalculate scores
            for trend in trends:
                try:
                    # Prepare data for scoring
                    score_data = {
                        "popularity_score": trend.popularity_score,
                        "growth_score": trend.growth_score,
                        "competition_score": trend.competition_score,
                        "opportunity_score": trend.opportunity_score,
                        "confidence_score": trend.confidence_score,
                        "detected_at": trend.detected_at
                    }
                    
                    # Calculate new scores
                    score_result = self.score_engine.calculate_score(score_data)
                    
                    # Update trend
                    self.repository.update_trend_score(
                        trend.id,
                        score_result.overall_score,
                        score_result.component_scores,
                        score_result.weighted_scores
                    )
                    
                    # Save score history
                    self.repository.save_score_history(
                        trend.trend_id,
                        score_data,
                        score_result.component_scores,
                        score_result.weighted_scores,
                        self.score_engine.weights.dict()
                    )
                    
                    # Invalidate cache
                    self.cache.invalidate_trend(trend.trend_id)
                    
                    trends_processed += 1
                    
                except Exception as e:
                    trends_failed += 1
                    continue
            
            # Invalidate analytics cache
            self.cache.delete(self.cache._make_key("analytics"))
            
            return {
                "success": True,
                "job_id": job_id,
                "trends_processed": trends_processed,
                "trends_failed": trends_failed,
                "message": f"Recalculated scores for {trends_processed} trends"
            }
            
        except Exception as e:
            return {
                "success": False,
                "job_id": job_id,
                "error": str(e),
                "trends_processed": trends_processed,
                "trends_failed": trends_failed
            }


class TaskQueue:
    """
    Simple task queue using Redis lists.
    
    Provides a basic queue system for background tasks.
    In production, consider using Celery or RQ for more robust task management.
    """
    
    def __init__(self, cache: TrendCache):
        """
        Initialize the task queue.
        
        Args:
            cache: Redis cache instance
        """
        self.cache = cache
        self.queue_key = "trend_intelligence:task_queue"
        self.processing_key = "trend_intelligence:processing"
    
    def enqueue(self, task_data: Dict[str, Any]) -> str:
        """
        Add a task to the queue.
        
        Args:
            task_data: Task data dictionary
            
        Returns:
            Task ID
        """
        task_id = task_data.get("task_id", str(uuid.uuid4()))
        task_data["task_id"] = task_id
        task_data["enqueued_at"] = datetime.utcnow().isoformat()
        
        self.cache.redis.rpush(self.queue_key, json.dumps(task_data))
        
        return task_id
    
    def dequeue(self, timeout: int = 5) -> Optional[Dict[str, Any]]:
        """
        Get a task from the queue.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Task data or None
        """
        result = self.cache.redis.blpop(self.queue_key, timeout=timeout)
        if result:
            task_json = result[1]
            return json.loads(task_json)
        return None
    
    def get_queue_length(self) -> int:
        """
        Get the current queue length.
        
        Returns:
            Number of tasks in queue
        """
        return self.cache.redis.llen(self.queue_key)
    
    def clear_queue(self) -> int:
        """
        Clear all tasks from the queue.
        
        Returns:
            Number of tasks cleared
        """
        return self.cache.redis.delete(self.queue_key)
