"""Recommendation record model."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

Priority = Literal["Critical", "High", "Medium", "Low"]


@dataclass(frozen=True)
class Recommendation:
    """Deterministic Finding → Impact → Action recommendation."""

    recommendation_id: str
    reporting_period: str
    module: str
    finding: str
    metric_name: str
    metric_value: float
    benchmark: float | str
    business_impact: str
    recommended_action: str
    priority: Priority
    responsible_department: str
    supporting_filters: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        """Serialize for UI consumers."""
        return asdict(self)
