"""
Repository for Store Builder Database Operations

This module handles all database operations for store blueprints.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.store import StoreBlueprint
from ..schemas.store import StoreCreateRequest


class StoreRepository:
    """Repository for store blueprint database operations."""
    
    def __init__(self, db: Session):
        """Initialize the repository."""
        self.db = db
    
    def create_store(self, store_data: Dict[str, Any]) -> StoreBlueprint:
        """Create a new store blueprint."""
        db_store = StoreBlueprint(
            user_id=store_data.get("user_id"),
            brand_profile_id=store_data["brand_profile_id"],
            product_id=store_data["product_id"],
            supplier_id=store_data.get("supplier_id"),
            store_name=store_data["store_name"],
            store_description=store_data["store_description"],
            tagline=store_data.get("tagline"),
            blueprint_json=store_data["blueprint_json"],
            validation_score=store_data.get("validation_score", 0),
            validation_result=store_data.get("validation_result"),
            metadata=store_data.get("metadata", {})
        )
        
        self.db.add(db_store)
        self.db.commit()
        self.db.refresh(db_store)
        
        return db_store
    
    def get_store_by_product(self, product_id: str) -> Optional[StoreBlueprint]:
        """Get a store by product ID."""
        return self.db.query(StoreBlueprint).filter(
            StoreBlueprint.product_id == product_id
        ).first()
    
    def get_store_by_id(self, store_id: int) -> Optional[StoreBlueprint]:
        """Get a store by database ID."""
        return self.db.query(StoreBlueprint).filter(
            StoreBlueprint.id == store_id
        ).first()
    
    def update_store(self, store_id: int, update_data: Dict[str, Any]) -> Optional[StoreBlueprint]:
        """Update a store blueprint."""
        db_store = self.get_store_by_id(store_id)
        if not db_store:
            return None
        
        for field, value in update_data.items():
            if hasattr(db_store, field):
                setattr(db_store, field, value)
        
        db_store.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_store)
        
        return db_store
    
    def delete_store(self, store_id: int) -> bool:
        """Delete a store blueprint."""
        db_store = self.get_store_by_id(store_id)
        if not db_store:
            return False
        
        self.db.delete(db_store)
        self.db.commit()
        
        return True
    
    def list_stores(self, skip: int = 0, limit: int = 20) -> tuple[List[StoreBlueprint], int]:
        """List all stores with pagination."""
        total = self.db.query(StoreBlueprint).count()
        stores = self.db.query(StoreBlueprint).order_by(
            desc(StoreBlueprint.created_at)
        ).offset(skip).limit(limit).all()
        
        return stores, total

    def list_stores_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> tuple[List[StoreBlueprint], int]:
        """List stores for a specific user."""
        query = self.db.query(StoreBlueprint).filter(StoreBlueprint.user_id == user_id)
        total = query.count()
        stores = query.order_by(desc(StoreBlueprint.created_at)).offset(skip).limit(limit).all()
        return stores, total
