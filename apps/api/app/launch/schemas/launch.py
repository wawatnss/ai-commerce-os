"""
Pydantic Schemas for the Launch module (admin "Create a new brand" wizard).
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
from enum import Enum


class BudgetTier(str, Enum):
    """Starting budget bracket, used to size the initial supplier offer."""
    STARTER = "starter"      # < $2,000
    GROWTH = "growth"        # $2,000 - $10,000
    SCALE = "scale"          # $10,000+


class Objective(str, Enum):
    """Primary goal for the new brand. Stored as metadata for future use."""
    SALES = "sales"                # Maximize sales / margin
    AWARENESS = "awareness"        # Build brand awareness
    SPEED = "speed"                # Launch as fast as possible


class LaunchRequest(BaseModel):
    """Input from the "Create a new brand" wizard."""
    name: str = Field(..., min_length=2, max_length=255, description="Working product/brand name")
    category: str = Field(..., min_length=2, max_length=100, description="Product category")
    objective: Objective = Field(default=Objective.SALES, description="Primary goal for this brand")
    budget: BudgetTier = Field(default=BudgetTier.GROWTH, description="Starting budget bracket")


class LaunchStepStatus(str, Enum):
    """Status of a single step of the launch pipeline."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class LaunchStep(BaseModel):
    """A single step of the launch pipeline, in execution order."""
    key: str = Field(..., description="Machine-readable step identifier")
    label: str = Field(..., description="Human-readable step label")
    status: LaunchStepStatus = Field(..., description="Step status")
    detail: Optional[str] = Field(None, description="Extra detail about the step result")
    duration_ms: Optional[int] = Field(None, description="How long the step took, in milliseconds")


class LaunchResponse(BaseModel):
    """Response returned by POST /api/v1/launch/generate."""
    success: bool = Field(..., description="Whether the full pipeline completed successfully")
    steps: List[LaunchStep] = Field(default_factory=list, description="Ordered pipeline steps")
    trend_id: Optional[str] = None
    supplier_id: Optional[str] = None
    brand_id: Optional[int] = None
    store_id: Optional[int] = Field(None, description="Generated store ID, used to redirect to /store-preview/{store_id}")
    store_name: Optional[str] = None
    readiness: Optional[Dict[str, Any]] = Field(None, description="Publication readiness report (Sprint 2.5)")
    shopify_readiness: Optional[Dict[str, Any]] = Field(None, description="Shopify import readiness report (Sprint 3A)")
    error: Optional[str] = Field(None, description="Error message if the pipeline failed")
