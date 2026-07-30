"""Display formatting helpers for Streamlit (no KPI math)."""

from __future__ import annotations

from src.analytics.types import KpiResult


def format_tzs(value: float, *, compact: bool = True) -> str:
    """Format a TZS amount for executive display."""
    if compact and abs(value) >= 1_000_000_000:
        return f"TZS {value / 1_000_000_000:,.2f}B"
    if compact and abs(value) >= 1_000_000:
        return f"TZS {value / 1_000_000:,.2f}M"
    return f"TZS {value:,.0f}"


def format_number(value: float, *, decimals: int = 1) -> str:
    """Format a generic numeric value with thousands separators."""
    if abs(value) >= 1000 and decimals == 0:
        return f"{value:,.0f}"
    if float(value).is_integer() and decimals == 0:
        return f"{int(value):,}"
    return f"{value:,.{decimals}f}"


def format_rate(value: float, *, decimals: int = 2) -> str:
    """Format a rate already expressed in percent units."""
    return f"{value:.{decimals}f}%"


def format_comparison(kpi: KpiResult) -> str:
    """Build a MoM/YoY comparison label for a KPI card."""
    if kpi.comparison_value is None or kpi.comparison_label is None:
        return "No prior period"
    value = kpi.comparison_value
    if kpi.comparison_method == "pp":
        sign = "+" if value > 0 else ""
        return f"{kpi.comparison_label} {sign}{value:.2f} pp"
    sign = "+" if value > 0 else ""
    return f"{kpi.comparison_label} {sign}{value:.1f}%"


def format_kpi_value(kpi: KpiResult) -> str:
    """Format the primary KPI value using its format hint."""
    if kpi.format_hint == "currency" or kpi.unit == "TZS":
        return format_tzs(kpi.value)
    if kpi.format_hint == "rate" or kpi.unit == "%":
        return format_rate(kpi.value)
    if kpi.format_hint == "integer":
        return format_number(kpi.value, decimals=0)
    return format_number(kpi.value, decimals=1)
