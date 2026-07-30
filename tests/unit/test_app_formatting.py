"""Unit tests for Streamlit formatting helpers (no Streamlit runtime)."""

from __future__ import annotations

import pandas as pd
from app.components.formatting import (
    format_comparison,
    format_kpi_value,
    format_number,
    format_rate,
    format_tzs,
)
from src.analytics.breakdowns import (
    filter_month_range,
    regional_revenue_slice,
    revenue_by_value_segment,
)
from src.analytics.types import KpiResult


def test_format_tzs_compact() -> None:
    assert format_tzs(1_500_000_000) == "TZS 1.50B"
    assert format_tzs(2_500_000) == "TZS 2.50M"
    assert "TZS" in format_tzs(12_500)


def test_format_kpi_and_comparison() -> None:
    kpi = KpiResult(
        name="Total Revenue",
        value=1_000_000,
        unit="TZS",
        reporting_month="2025-12-01",
        comparison_label="MoM",
        comparison_value=5.0,
        comparison_method="pct",
        format_hint="currency",
    )
    assert format_kpi_value(kpi) == "TZS 1.00M"
    assert format_comparison(kpi) == "MoM +5.0%"

    churn = KpiResult(
        name="Churn Rate",
        value=0.15,
        unit="%",
        reporting_month="2025-12-01",
        comparison_label="MoM",
        comparison_value=-0.05,
        comparison_method="pp",
        format_hint="rate",
    )
    assert format_rate(churn.value) == "0.15%"
    assert "pp" in format_comparison(churn)
    assert format_number(1200, decimals=0) == "1,200"


def test_breakdown_helpers() -> None:
    executive = pd.DataFrame(
        {
            "reporting_month": ["2025-10-01", "2025-11-01", "2025-12-01"],
            "total_revenue": [1.0, 2.0, 3.0],
        }
    )
    trimmed = filter_month_range(
        executive, start_month="2025-11-01", end_month="2025-12-01"
    )
    assert list(trimmed["reporting_month"]) == ["2025-11-01", "2025-12-01"]

    regional = pd.DataFrame(
        {
            "reporting_month": ["2025-12-01", "2025-12-01"],
            "region": ["Arusha", "Geita"],
            "subscribers": [10, 20],
            "total_revenue": [100.0, 50.0],
            "arpu": [10.0, 2.5],
        }
    )
    sliced = regional_revenue_slice(
        regional, reporting_month="2025-12-01", regions=["Arusha"]
    )
    assert len(sliced) == 1
    assert sliced.iloc[0]["region"] == "Arusha"

    snapshot = pd.DataFrame(
        {
            "reporting_month": ["2025-12-01", "2025-12-01", "2025-11-01"],
            "value_segment": ["High Value", "Mass", "High Value"],
            "total_revenue": [10.0, 20.0, 99.0],
            "customers": [1, 1, 1],
        }
    )
    by_seg = revenue_by_value_segment(snapshot, reporting_month="2025-12-01")
    high = by_seg.loc[by_seg["value_segment"] == "High Value", "total_revenue"].iloc[0]
    assert float(high) == 10.0
