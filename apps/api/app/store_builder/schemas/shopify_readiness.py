"""
Pydantic schemas for the Shopify Readiness Report (Sprint 3A).
"""

from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class ShopifyReadinessStatus(str, Enum):
    """Result of a single Shopify readiness check."""
    PASS = "pass"
    PARTIAL = "partial"
    FAIL = "fail"


class ShopifyReadinessCheck(BaseModel):
    """One item of the Shopify readiness checklist."""
    key: str
    label: str
    status: ShopifyReadinessStatus
    score: int
    max_score: int
    message: str = ""


class ShopifyReadinessReport(BaseModel):
    """Full Shopify readiness report for a store blueprint."""
    overall_score: int = Field(..., ge=0, le=100)
    checks: List[ShopifyReadinessCheck]
    remaining_actions: List[str]
    is_ready: bool = Field(default=False, description="True when score >= 85 and no fail")
