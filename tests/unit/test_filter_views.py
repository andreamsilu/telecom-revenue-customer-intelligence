"""Unit tests for dashboard filter application helpers."""

from __future__ import annotations

import pandas as pd
from src.analytics.filter_views import (
    FilterSelection,
    apply_campaign_filters,
    apply_regional_filter,
    apply_segment_filter,
    customer_base_metrics,
    regional_month_slice,
    scoped_revenue_trend,
    segment_month_slice,
)


def _selection(**kwargs: object) -> FilterSelection:
    base = {
        "reporting_month": "2025-12-01",
        "start_month": "2025-01-01",
        "end_month": "2025-12-01",
    }
    base.update(kwargs)
    return FilterSelection(**base)  # type: ignore[arg-type]


def test_regional_and_segment_filters() -> None:
    regional = pd.DataFrame(
        {
            "reporting_month": ["2025-12-01", "2025-12-01", "2025-11-01"],
            "region": ["Arusha", "Geita", "Arusha"],
            "subscribers": [10, 20, 9],
            "active_subscribers": [8, 15, 7],
            "total_revenue": [100.0, 50.0, 90.0],
            "newly_churned": [1, 2, 0],
            "recharge_value": [40.0, 20.0, 30.0],
            "arpu": [12.5, 3.3, 12.8],
        }
    )
    selection = _selection(regions=("Arusha",))
    filtered = apply_regional_filter(regional, selection)
    assert set(filtered["region"]) == {"Arusha"}
    month = regional_month_slice(regional, selection)
    assert len(month) == 1
    assert float(month.iloc[0]["total_revenue"]) == 100.0

    segments = pd.DataFrame(
        {
            "reporting_month": ["2025-12-01", "2025-12-01"],
            "value_segment": ["High Value", "Low Value"],
            "total_revenue": [80.0, 20.0],
            "customers": [5, 10],
        }
    )
    seg_sel = _selection(value_segments=("High Value",))
    assert len(apply_segment_filter(segments, seg_sel)) == 1
    assert (
        segment_month_slice(segments, seg_sel).iloc[0]["value_segment"] == "High Value"
    )


def test_campaign_and_base_metrics() -> None:
    campaigns = pd.DataFrame(
        {
            "campaign_id": ["A", "B"],
            "target_region": ["Arusha", "Geita"],
            "target_segment": ["High Value", "Youth"],
            "promoted_product": ["data_bundle", "voice"],
            "roi": [0.1, -0.2],
        }
    )
    selection = _selection(regions=("Arusha",), product_categories=("data",))
    out = apply_campaign_filters(campaigns, selection)
    assert list(out["campaign_id"]) == ["A"]

    dim = pd.DataFrame(
        {
            "customer_id": ["1", "2", "3"],
            "region": ["Arusha", "Geita", "Arusha"],
            "value_segment": ["High Value", "Low Value", "High Value"],
            "account_type": ["Prepaid", "Postpaid", "Prepaid"],
        }
    )
    matched, total, share = customer_base_metrics(
        dim, _selection(regions=("Arusha",), account_types=("Prepaid",))
    )
    assert matched == 2
    assert total == 3
    assert share > 60.0


def test_scoped_revenue_trend_aggregates_regions() -> None:
    national = pd.DataFrame(
        {
            "reporting_month": ["2025-11-01", "2025-12-01"],
            "total_revenue": [1000.0, 1100.0],
            "arpu": [50.0, 55.0],
            "total_subscribers": [100, 110],
        }
    )
    regional = pd.DataFrame(
        {
            "reporting_month": ["2025-11-01", "2025-11-01", "2025-12-01"],
            "region": ["Arusha", "Geita", "Arusha"],
            "subscribers": [10, 20, 12],
            "active_subscribers": [8, 15, 10],
            "total_revenue": [40.0, 60.0, 50.0],
        }
    )
    trend = scoped_revenue_trend(
        national_mart=national,
        regional_mart=regional,
        selection=_selection(regions=("Arusha",)),
    )
    dec = trend[trend["reporting_month"] == "2025-12-01"].iloc[0]
    assert float(dec["total_revenue"]) == 50.0
