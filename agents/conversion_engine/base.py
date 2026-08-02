"""
Base class shared by every sub-optimizer.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from .models import OptimizerResult


class BaseOptimizer(ABC):
    """
    A sub-optimizer analyzes (and, for most, also improves in place) a store
    blueprint dict, and always returns an `OptimizerResult` describing what
    it found/changed.

    Some optimizers are analysis-only (UXOptimizer, PricingOptimizer) and
    never mutate the blueprint; this is documented on each subclass.
    """

    name: str = "base"

    @abstractmethod
    def optimize(self, blueprint: Dict[str, Any]) -> OptimizerResult:
        """Analyze (and possibly improve) the blueprint in place."""
        raise NotImplementedError
