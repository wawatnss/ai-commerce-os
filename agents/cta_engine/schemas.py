"""Pydantic schemas for the CTA Engine."""

from pydantic import BaseModel, Field
from typing import List


class CTAVariant(BaseModel):
    label: str
    context: str
    predicted_score: float = Field(..., ge=0, le=100)
    tone: str


class CTASet(BaseModel):
    hero: CTAVariant
    product: CTAVariant
    newsletter: CTAVariant
    urgency: CTAVariant
    trust: CTAVariant
    all_variants: List[CTAVariant]
