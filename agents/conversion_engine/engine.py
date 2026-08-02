"""
ConversionEngine

Facade that runs every sub-optimizer over a store blueprint and compiles a
single ConversionReport.
"""

import copy
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from .models import ConversionReport, OptimizerResult, Suggestion, clamp_score
from .hero_optimizer import HeroOptimizer
from .trust_optimizer import TrustOptimizer
from .product_page_optimizer import ProductPageOptimizer
from .pricing_optimizer import PricingOptimizer
from .review_optimizer import ReviewOptimizer
from .ux_optimizer import UXOptimizer
from .seo_optimizer import SEOOptimizer

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}


class ConversionEngine:
    """
    Runs Hero, Trust, ProductPage, Reviews and SEO optimizers (which improve
    the blueprint in place), plus UX and Pricing (analysis-only, the latter
    NEVER touches actual prices), then compiles a ConversionReport.
    """

    def __init__(self) -> None:
        self.hero = HeroOptimizer()
        self.trust = TrustOptimizer()
        self.product_page = ProductPageOptimizer()
        self.pricing = PricingOptimizer()
        self.reviews = ReviewOptimizer()
        self.ux = UXOptimizer()
        self.seo = SEOOptimizer()

    def run(self, blueprint: Dict[str, Any], demo_mode: bool = False) -> Tuple[Dict[str, Any], ConversionReport]:
        """
        Run the full pipeline over a copy of `blueprint` and return
        `(optimized_blueprint, report)`. The input blueprint is never
        mutated - callers decide whether/how to persist the result.
        """
        working_blueprint = copy.deepcopy(blueprint)

        results: List[OptimizerResult] = [
            self.hero.optimize(working_blueprint),
            self.trust.optimize(working_blueprint),
            self.product_page.optimize(working_blueprint),
            self.reviews.optimize(working_blueprint, demo_mode=demo_mode),
            self.seo.optimize(working_blueprint),
            self.ux.optimize(working_blueprint),          # analysis-only
            self.pricing.optimize(working_blueprint),      # analysis-only, never touches prices
        ]

        report = self._compile_report(results, demo_mode)
        working_blueprint["conversion_report"] = report.to_dict()
        return working_blueprint, report

    def _compile_report(self, results: List[OptimizerResult], demo_mode: bool) -> ConversionReport:
        scores = {r.optimizer: r.score for r in results}

        seo_score = scores.get("seo", 0.0)
        ux_score = scores.get("ux", 0.0)
        trust_score = scores.get("trust", 0.0)
        persuasion_score = clamp_score(
            (scores.get("hero", 0.0) + scores.get("product_page", 0.0) + scores.get("reviews", 0.0)) / 3
        )
        conversion_score = clamp_score(
            seo_score * 0.2 + ux_score * 0.2 + trust_score * 0.25 + persuasion_score * 0.35
        )

        all_suggestions: List[Suggestion] = [s for r in results for s in r.suggestions]
        all_suggestions.sort(key=lambda s: SEVERITY_ORDER.get(s.severity, 9))

        strengths = [
            f"{r.optimizer.replace('_', ' ').title()} is well optimized (score {r.score:.0f}/100)"
            for r in results if r.score >= 90
        ]
        weaknesses = [
            f"{r.optimizer.replace('_', ' ').title()} needs improvement (score {r.score:.0f}/100)"
            for r in results if r.score < 70
        ]

        return ConversionReport(
            conversion_score=conversion_score,
            seo_score=seo_score,
            ux_score=ux_score,
            trust_score=trust_score,
            persuasion_score=persuasion_score,
            strengths=strengths or ["No standout strengths yet - address the recommended actions and re-run the analysis."],
            weaknesses=weaknesses or ["No major weaknesses detected."],
            recommended_actions=all_suggestions,
            optimizer_results=results,
            generated_at=datetime.now(timezone.utc).isoformat(),
            demo_mode=demo_mode,
        )
