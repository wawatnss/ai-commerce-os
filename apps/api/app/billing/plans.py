"""Plan definitions."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Plan:
    slug: str
    name: str
    max_stores: int
    max_exports: int
    max_generations: int
    ai_credits: int
    support: str


PLANS: Dict[str, Plan] = {
    "free": Plan(
        slug="free",
        name="Free",
        max_stores=3,
        max_exports=1,
        max_generations=5,
        ai_credits=0,
        support="community",
    ),
    "pro": Plan(
        slug="pro",
        name="Pro",
        max_stores=25,
        max_exports=10,
        max_generations=50,
        ai_credits=500,
        support="email",
    ),
    "business": Plan(
        slug="business",
        name="Business",
        max_stores=-1,  # unlimited
        max_exports=-1,
        max_generations=-1,
        ai_credits=5000,
        support="priority",
    ),
}
