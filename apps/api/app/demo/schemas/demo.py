"""
Pydantic Schemas for the Demo module.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class DemoStepStatus(str, Enum):
    """Status of a single step of the demo pipeline."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DemoStep(BaseModel):
    """A single step of the demo generation pipeline, in execution order."""
    key: str = Field(..., description="Machine-readable step identifier")
    label: str = Field(..., description="Human-readable step label")
    status: DemoStepStatus = Field(..., description="Step status")
    detail: Optional[str] = Field(None, description="Extra detail about the step result")
    duration_ms: Optional[int] = Field(None, description="How long the step took, in milliseconds")


class DemoGenerateResponse(BaseModel):
    """Response returned by POST /api/v1/demo/generate."""
    success: bool = Field(..., description="Whether the full pipeline completed successfully")
    steps: List[DemoStep] = Field(default_factory=list, description="Ordered pipeline steps")
    trend_id: Optional[str] = Field(None, description="Generated trend_id")
    product_report_id: Optional[int] = Field(None, description="Generated product intelligence report ID")
    supplier_id: Optional[str] = Field(None, description="Generated supplier ID")
    brand_id: Optional[int] = Field(None, description="Generated brand profile ID")
    store_id: Optional[int] = Field(None, description="Generated store ID, used to redirect to /store-preview/{store_id}")
    error: Optional[str] = Field(None, description="Error message if the pipeline failed")
