"""
Mock Provider for Testing and Development

This is a sample implementation of BaseProvider that generates mock trend data.
It serves as a template for implementing real providers and can be used for testing.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
from .base import BaseProvider, TrendItem, CollectionError, NormalizationError


class MockProvider(BaseProvider):
    """
    Mock provider that generates sample trend data for testing.
    
    This provider simulates data collection from a trend source and
    generates realistic-looking trend data for development and testing purposes.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.sample_categories = [
            "electronics", "fashion", "home", "beauty", "sports",
            "automotive", "books", "toys", "health", "food"
        ]
        self.sample_products = [
            "wireless earbuds", "smart watch", "yoga mat", "coffee maker",
            "running shoes", "skincare set", "backpack", "desk lamp",
            "water bottle", "phone case", "laptop stand", "bluetooth speaker"
        ]
        self.sample_brands = [
            "TechBrand", "StyleCo", "HomeEssentials", "BeautyPro",
            "SportMax", "AutoTech", None, None  # Some items may not have brands
        ]
    
    async def collect(self, category: Optional[str] = None, limit: int = 50, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect mock trend data.
        
        Args:
            category: Filter by category (optional)
            limit: Maximum number of items to return
            **kwargs: Additional parameters (ignored in mock)
            
        Returns:
            List of raw trend data dictionaries
            
        Raises:
            CollectionError: If collection fails
        """
        try:
            if limit <= 0 or limit > 1000:
                raise CollectionError("Limit must be between 1 and 1000")
            
            # Generate mock data
            raw_data = []
            for i in range(limit):
                product = random.choice(self.sample_products)
                cat = category or random.choice(self.sample_categories)
                brand = random.choice(self.sample_brands)
                
                raw_data.append({
                    "id": f"mock_{i}_{int(datetime.utcnow().timestamp())}",
                    "product_name": product,
                    "brand": brand,
                    "category": cat,
                    "search_volume": random.randint(1000, 100000),
                    "growth_rate": random.uniform(-10, 100),
                    "competition_index": random.uniform(0, 100),
                    "timestamp": datetime.utcnow() - timedelta(hours=random.randint(0, 24))
                })
            
            return raw_data
            
        except Exception as e:
            raise CollectionError(f"Failed to collect mock data: {str(e)}")
    
    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[TrendItem]:
        """
        Normalize mock data into TrendItem format.
        
        Args:
            raw_data: Raw data from collect()
            
        Returns:
            List of normalized TrendItem objects
            
        Raises:
            NormalizationError: If normalization fails
        """
        try:
            normalized_items = []
            
            for item in raw_data:
                # Calculate scores from raw data
                search_volume = item.get("search_volume", 0)
                growth_rate = item.get("growth_rate", 0)
                competition_index = item.get("competition_index", 50)
                
                # Normalize search volume to 0-100 scale
                popularity_score = min(100, (search_volume / 100000) * 100)
                
                # Normalize growth rate to 0-100 scale
                growth_score = max(0, min(100, growth_rate))
                
                # Competition is already 0-100
                competition_score = competition_index
                
                # Calculate opportunity score (high growth + low competition)
                opportunity_score = (growth_score * 0.6) + ((100 - competition_score) * 0.4)
                
                # Confidence score based on data freshness
                timestamp = item.get("timestamp", datetime.utcnow())
                hours_old = (datetime.utcnow() - timestamp).total_seconds() / 3600
                confidence_score = max(0, 100 - (hours_old * 2))
                
                # Generate tags from product name
                product_name = item.get("product_name", "")
                tags = [product_name.lower(), item.get("category", "").lower()]
                
                trend_item = TrendItem(
                    id=item["id"],
                    source=self.provider_name,
                    product_name=product_name,
                    brand=item.get("brand"),
                    category=item.get("category"),
                    tags=tags,
                    popularity_score=round(popularity_score, 2),
                    growth_score=round(growth_score, 2),
                    competition_score=round(competition_score, 2),
                    opportunity_score=round(opportunity_score, 2),
                    confidence_score=round(confidence_score, 2),
                    detected_at=timestamp,
                    metadata={
                        "raw_search_volume": search_volume,
                        "raw_growth_rate": growth_rate,
                        "collection_timestamp": timestamp.isoformat()
                    }
                )
                
                normalized_items.append(trend_item)
            
            return normalized_items
            
        except Exception as e:
            raise NormalizationError(f"Failed to normalize data: {str(e)}")
    
    def validate(self, trend_item: TrendItem) -> bool:
        """
        Validate a TrendItem.
        
        Args:
            trend_item: The TrendItem to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if not trend_item.product_name or not trend_item.category:
            return False
        
        # Check score ranges
        if not (0 <= trend_item.popularity_score <= 100):
            return False
        if not (0 <= trend_item.growth_score <= 100):
            return False
        if not (0 <= trend_item.competition_score <= 100):
            return False
        if not (0 <= trend_item.opportunity_score <= 100):
            return False
        if not (0 <= trend_item.confidence_score <= 100):
            return False
        
        # Check for reasonable data
        if trend_item.detected_at > datetime.utcnow():
            return False
        
        return True
