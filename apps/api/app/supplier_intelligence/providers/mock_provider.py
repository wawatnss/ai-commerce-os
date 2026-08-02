"""
Mock Supplier Provider

This module provides a mock implementation of the supplier provider for testing and development.
"""

from typing import Dict, Any, List, Optional
from .base import BaseSupplierProvider, SupplierData, SupplierOfferData


class MockSupplierProvider(BaseSupplierProvider):
    """
    Mock provider for supplier data.
    
    Generates sample supplier and offer data for testing and development.
    In production, this would be replaced by real providers (API integrations, etc.).
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._mock_suppliers = {
            "SUPP001": SupplierData(
                name="Global Trading Co",
                source="mock",
                country="China",
                currency="USD",
                contact={"email": "contact@globaltrading.com", "phone": "+86-123-4567"},
                metadata={"tier": "premium", "established": 2010}
            ),
            "SUPP002": SupplierData(
                name="Asia Export Ltd",
                source="mock",
                country="Vietnam",
                currency="USD",
                contact={"email": "sales@asiaexport.com"},
                metadata={"tier": "standard", "established": 2015}
            ),
            "SUPP003": SupplierData(
                name="EuroSource GmbH",
                source="mock",
                country="Germany",
                currency="EUR",
                contact={"email": "info@eurosource.de"},
                metadata={"tier": "premium", "established": 2005}
            ),
            "SUPP004": SupplierData(
                name="Pacific Supplies",
                source="mock",
                country="Taiwan",
                currency="USD",
                contact={"email": "orders@pacificsupplies.com"},
                metadata={"tier": "standard", "established": 2018}
            ),
            "SUPP005": SupplierData(
                name="MexTrade SA",
                source="mock",
                country="Mexico",
                currency="USD",
                contact={"email": "ventas@mextrade.mx"},
                metadata={"tier": "standard", "established": 2012}
            )
        }
    
    def collect_suppliers(self, filters: Optional[Dict[str, Any]] = None) -> List[SupplierData]:
        """
        Collect mock supplier data.
        
        Args:
            filters: Optional filters (country, tier, etc.)
            
        Returns:
            List of supplier data
        """
        suppliers = list(self._mock_suppliers.values())
        
        if filters:
            if "country" in filters:
                suppliers = [s for s in suppliers if s.country == filters["country"]]
            if "tier" in filters:
                suppliers = [s for s in suppliers if s.metadata.get("tier") == filters["tier"]]
        
        return suppliers
    
    def collect_offers(
        self,
        product_id: str,
        supplier_ids: Optional[List[str]] = None
    ) -> List[SupplierOfferData]:
        """
        Collect mock supplier offers for a product.
        
        Args:
            product_id: Product identifier
            supplier_ids: Optional list of supplier IDs
            
        Returns:
            List of offer data
        """
        # Generate mock offers based on product_id
        # In production, this would query real supplier APIs
        target_suppliers = supplier_ids if supplier_ids else list(self._mock_suppliers.keys())
        
        offers = []
        for supplier_id in target_suppliers:
            if supplier_id not in self._mock_suppliers:
                continue
            
            # Generate mock offer data with some variation
            base_cost = 10.0 + (hash(product_id) % 50)  # Deterministic but varied
            supplier_modifier = (hash(supplier_id) % 10) / 10.0
            
            offers.append(SupplierOfferData(
                supplier_id=supplier_id,
                product_id=product_id,
                unit_cost=round(base_cost * (1 + supplier_modifier), 2),
                minimum_order_quantity=10 + (hash(supplier_id) % 90),
                estimated_processing_time=3 + (hash(supplier_id) % 5),
                estimated_shipping_time=7 + (hash(supplier_id) % 14),
                available_quantity=100 + (hash(product_id) % 900),
                currency=self._mock_suppliers[supplier_id].currency,
                metadata={"last_sync": "2026-08-01"}
            ))
        
        return offers
