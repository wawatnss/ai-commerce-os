"""
Engines Module Initialization

Exports all brand generation engines.
"""

from .base import BaseBrandEngine, EngineResult, EngineError, GenerationError
from .name_engine import NameEngine
from .audience_engine import AudienceEngine
from .identity_engine import IdentityEngine
from .visual_engine import VisualEngine
from .messaging_engine import MessagingEngine
from .positioning_engine import PositioningEngine

# Validator is in a separate file, import it separately
try:
    from .validator import BrandValidator, ValidationResult
    __all__ = [
        "BaseBrandEngine",
        "EngineResult",
        "EngineError",
        "GenerationError",
        "NameEngine",
        "AudienceEngine",
        "IdentityEngine",
        "VisualEngine",
        "MessagingEngine",
        "PositioningEngine",
        "BrandValidator",
        "ValidationResult",
    ]
except ImportError:
    __all__ = [
        "BaseBrandEngine",
        "EngineResult",
        "EngineError",
        "GenerationError",
        "NameEngine",
        "AudienceEngine",
        "IdentityEngine",
        "VisualEngine",
        "MessagingEngine",
        "PositioningEngine",
    ]
