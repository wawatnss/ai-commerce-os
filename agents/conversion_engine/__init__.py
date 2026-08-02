"""
Conversion Optimization Engine

Turns a "correct" store blueprint (as produced by apps/api's Store Builder)
into one optimized to sell, by running a set of independent sub-optimizers
and compiling their results into a single Conversion Report.

This module has zero external dependencies (no AI provider, no database, no
web framework) so it can be unit tested in isolation and reused from
anywhere: the FastAPI backend, seed_demo.py, a CLI, a background job, etc.

Usage:
    from agents.conversion_engine import ConversionEngine

    engine = ConversionEngine()
    optimized_blueprint, report = engine.run(blueprint, demo_mode=False)
"""

from .engine import ConversionEngine
from .models import ConversionReport, OptimizerResult, Suggestion
from .hero_optimizer import HeroOptimizer
from .trust_optimizer import TrustOptimizer
from .product_page_optimizer import ProductPageOptimizer
from .pricing_optimizer import PricingOptimizer
from .review_optimizer import ReviewOptimizer
from .ux_optimizer import UXOptimizer
from .seo_optimizer import SEOOptimizer

__all__ = [
    "ConversionEngine",
    "ConversionReport",
    "OptimizerResult",
    "Suggestion",
    "HeroOptimizer",
    "TrustOptimizer",
    "ProductPageOptimizer",
    "PricingOptimizer",
    "ReviewOptimizer",
    "UXOptimizer",
    "SEOOptimizer",
]
