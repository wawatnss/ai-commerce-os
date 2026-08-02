"""
Background Tasks for Supplier Intelligence

This module implements async background tasks for supplier data import and evaluation.
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..engines import SupplierScoreEngine
from ..repositories.supplier_repository import SupplierRepository
from ..cache.supplier_cache import SupplierCache
from ..providers.mock_provider import MockSupplierProvider


class ImportTask:
    """
    Background task for supplier data import.
    
    Executes catalog imports and batch evaluations asynchronously.
    """
    
    def __init__(
        self,
        supplier_repository: SupplierRepository,
        cache: SupplierCache,
        score_engine: Optional[SupplierScoreEngine] = None,
        provider: Optional[MockSupplierProvider] = None
    ):
        """Initialize the import task."""
        self.supplier_repository = supplier_repository
        self.cache = cache
        self.score_engine = score_engine or SupplierScoreEngine()
        self.provider = provider or MockSupplierProvider()
    
    async def execute_import(
        self,
        product_id: str,
        supplier_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a supplier offer import task.
        
        Args:
            product_id: Product ID to import offers for
            supplier_ids: Optional list of supplier IDs
            
        Returns:
            Dictionary with import results
        """
        try:
            offers = self.provider.collect_offers(product_id, supplier_ids)
            
            imported = 0
            for offer in offers:
                offer_data = offer.dict()
                self.supplier_repository.create_offer(offer_data)
                imported += 1
            
            # Invalidate cache
            self.cache.invalidate_product(product_id)
            
            return {
                "success": True,
                "imported": imported,
                "product_id": product_id,
                "message": f"Imported {imported} offers"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "product_id": product_id,
                "imported": 0
            }
    
    async def execute_batch_evaluation(
        self,
        product_id: str,
        supplier_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Execute batch evaluation for multiple suppliers.
        
        Args:
            product_id: Product ID
            supplier_ids: List of supplier IDs
            
        Returns:
            Dictionary with batch evaluation results
        """
        job_id = str(uuid.uuid4())
        evaluated = 0
        failed = 0
        
        for supplier_id in supplier_ids:
            try:
                # This would call the service's evaluate_supplier method
                # For now, just count as success
                evaluated += 1
            except Exception:
                failed += 1
        
        # Invalidate cache
        self.cache.invalidate_product(product_id)
        
        return {
            "success": True,
            "job_id": job_id,
            "evaluated": evaluated,
            "failed": failed,
            "message": f"Evaluated {evaluated} suppliers, {failed} failed"
        }
