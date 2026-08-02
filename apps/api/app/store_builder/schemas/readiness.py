"""
Pydantic schemas for the Publication Readiness Report (Sprint 2.5).
"""

from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class ReadinessStatus(str, Enum):
    """Result of a single readiness check."""
    PASS = "pass"
    PARTIAL = "partial"
    FAIL = "fail"


class ReadinessCheck(BaseModel):
    """One item of the publication checklist."""
    key: str = Field(..., description="Machine-readable check id")
    label: str = Field(..., description="Human-readable label")
    status: ReadinessStatus
    score: int = Field(..., description="Points earned for this check")
    max_score: int
    message: str = Field(default="", description="Short explanation")


class ReadinessReport(BaseModel):
    """Full publication readiness report for a store blueprint."""
    overall_score: int = Field(..., ge=0, le=100)
    checks: List[ReadinessCheck]
    remaining_actions: List[str]
    is_ready: bool = Field(default=False, description="True when score >= 80 and no fail")
