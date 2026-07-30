"""Shared analytics result types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ComparisonMethod = Literal["pct", "pp", "absolute"]


@dataclass(frozen=True)
class KpiResult:
    """A single KPI value with an optional period comparison."""

    name: str
    value: float
    unit: str
    reporting_month: str
    comparison_label: str | None = None
    comparison_value: float | None = None
    comparison_method: ComparisonMethod | None = None
    format_hint: str = "number"

    def as_dict(self) -> dict[str, object]:
        """Serialize for UI/service consumers."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "reporting_month": self.reporting_month,
            "comparison_label": self.comparison_label,
            "comparison_value": self.comparison_value,
            "comparison_method": self.comparison_method,
            "format_hint": self.format_hint,
        }
