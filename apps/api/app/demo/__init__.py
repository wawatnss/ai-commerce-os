"""
Demo Module

Provides a fully self-contained, end-to-end demo pipeline that showcases the
whole platform (Trend Intelligence -> Product Intelligence -> Supplier
Intelligence -> Brand Builder -> Store Builder) without requiring any
external API (no OpenAI/Anthropic calls, no third-party data providers).
"""

from .api.router import router

__all__ = ["router"]
