"""Pydantic schemas for the FAQ Engine."""

from pydantic import BaseModel
from typing import List


class FAQItem(BaseModel):
    question: str
    answer: str
    category: str


class FAQSet(BaseModel):
    items: List[FAQItem]
    diversity_score: float
