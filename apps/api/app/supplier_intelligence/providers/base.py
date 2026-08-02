"""
Base Provider Interface for Supplier Intelligence

This module defines the abstract base class for supplier data providers.
This enables future integration with official APIs or data imports without
modifying the core system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SupplierData(BaseModel):
    """Standardized supplier data model."""
    name: str = Field(..., description="Supplier name")
    source: str = Field(..., description="Data source identifier")
    country: Optional[str] = Field(None, description="Supplier country")
    currency: Optional[str] = Field(None, description="Preferred currency")
    contact: Optional[Dict[str, str]] = Field(None, description="Contact information")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SupplierOfferData(BaseModel):
    """Standardized supplier offer data model."""
    supplier_id: str = Field(..., description="Supplier identifier")
    product_id: str = Field(..., description="Product identifier")
    unit_cost: float = Field(..., ge=0, description="Unit cost")
    minimum_order_quantity: int = Field(..., ge=1, description="Minimum order quantity")
    estimated_processing_time: int = Field(..., ge=0, description="Processing time in days")
    estimated_shipping_time: int = Field(..., ge=0, description="Shipping time in days")
    available_quantity: Optional[int] = Field(None, ge=0, description="Available quantity")
    currency: Optional[str] = Field(None, description="Currency for unit_cost")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BaseSupplierProvider(ABC):
    """
    Abstract base class for supplier data providers.
    
    This interface allows integration with various data sources:
    - Official platform APIs (Alibaba, AliExpress, etc.)
    - CSV/XML imports
    - Database exports
    - Custom integrations
    
    All providers must implement the collect() method to return standardized data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the provider.
        
        Args:
            config: Optional provider configuration
        """
        self.config = config or {}
        self.provider_name = self.__class__.__name__.replace("Provider", "")
    
    @abstractmethod
    def collect_suppliers(self, filters: Optional[Dict[str, Any]] = None) -> List[SupplierData]:
        """
        Collect supplier data from the source.
        
        Args:
            filters: Optional filters for data collection
            
        Returns:
            List of standardized supplier data
        """
        pass
    
    @abstractmethod
    def collect_offers(
        self,
        product_id: str,
        supplier_ids: Optional[List[str]] = None
    ) -> List[SupplierOfferData]:
        """
        Collect supplier offers for a specific product.
        
        Args:
            product_id: Product identifier
            supplier_ids: Optional list of supplier IDs to collect offers for
            
        Returns:
            List of standardized offer data
        """
        pass
    
    def get_name(self) -> str:
        """Get the provider name."""
        return self.provider_name
    
    def get_config(self) -> Dict[str, Any]:
        """Get the provider configuration."""
        return self.config
    
    def validate(self) -> bool:
        """
        Validate the provider configuration.
        
        Returns:
            True if configuration is valid
        """
        return True


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class CollectionError(ProviderError):
    """Raised when data collection fails."""
    pass


class ValidationError(ProviderError):
    """Raised when data validation fails."""
    pass
