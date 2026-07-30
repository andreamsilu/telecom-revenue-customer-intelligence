"""Deterministic executive recommendation engine package."""

from src.recommendations.engine import generate_recommendations
from src.recommendations.models import Recommendation

__all__ = ["Recommendation", "generate_recommendations"]
