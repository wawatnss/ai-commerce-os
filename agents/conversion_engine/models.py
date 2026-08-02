"""
Plain-data models shared by every sub-optimizer and the Conversion Report.

Kept as stdlib `dataclasses` (no pydantic/FastAPI dependency) so this
package stays framework-agnostic; the API layer is responsible for wrapping
`.to_dict()` output into whatever response schema it needs.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

Severity = str  # "high" | "medium" | "low" | "info"


@dataclass
class Suggestion:
    """A single, actionable recommendation produced by an optimizer."""

    id: str
    optimizer: str
    severity: Severity
    title: str
    description: str
    applied: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "optimizer": self.optimizer,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "applied": self.applied,
        }


@dataclass
class OptimizerResult:
    """The output of running a single sub-optimizer."""

    optimizer: str
    score: float
    suggestions: List[Suggestion] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "optimizer": self.optimizer,
            "score": round(self.score, 2),
            "suggestions": [s.to_dict() for s in self.suggestions],
            "details": self.details,
        }


@dataclass
class ConversionReport:
    """Aggregate report produced by the ConversionEngine."""

    conversion_score: float
    seo_score: float
    ux_score: float
    trust_score: float
    persuasion_score: float
    strengths: List[str]
    weaknesses: List[str]
    recommended_actions: List[Suggestion]
    optimizer_results: List[OptimizerResult]
    generated_at: str
    demo_mode: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversion_score": round(self.conversion_score, 2),
            "seo_score": round(self.seo_score, 2),
            "ux_score": round(self.ux_score, 2),
            "trust_score": round(self.trust_score, 2),
            "persuasion_score": round(self.persuasion_score, 2),
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommended_actions": [s.to_dict() for s in self.recommended_actions],
            "optimizer_results": [r.to_dict() for r in self.optimizer_results],
            "generated_at": self.generated_at,
            "demo_mode": self.demo_mode,
        }


def clamp_score(score: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    """Keep a score within [minimum, maximum]."""
    return max(minimum, min(maximum, score))
