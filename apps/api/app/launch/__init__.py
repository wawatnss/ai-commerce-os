"""
Launch Module

Powers the admin dashboard's "Create a new brand" wizard: given a name,
category, objective and budget, runs the exact same underlying pipeline as
app.demo (Trend -> Product -> Supplier -> Brand -> Store -> Optimize), but
driven by real user input instead of a random demo product, and without
ever using demo-only shortcuts (e.g. simulated reviews).
"""

from .api.router import router

__all__ = ["router"]
