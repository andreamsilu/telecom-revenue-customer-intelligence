"""Unit tests for analytics comparison helpers."""

from __future__ import annotations

import pytest
from src.analytics.comparisons import (
    absolute_change,
    percent_change,
    percentage_point_change,
    period_snapshot,
)


def test_percent_change_basic() -> None:
    assert percent_change(110.0, 100.0) == 10.0
    assert percent_change(90.0, 100.0) == -10.0
    assert percent_change(10.0, None) is None
    assert percent_change(10.0, 0.0) is None


def test_percentage_point_change_for_rates() -> None:
    assert percentage_point_change(4.8, 5.4) == pytest.approx(-0.6)
    assert percentage_point_change(12.0, None) is None


def test_absolute_change() -> None:
    assert absolute_change(15.0, 10.0) == 5.0


def test_period_snapshot_reads_mart_columns() -> None:
    row = {
        "total_revenue": 200.0,
        "total_revenue_previous_month_value": 100.0,
        "total_revenue_prior_year_value": 150.0,
        "total_revenue_rolling_3_month_average": 180.0,
        "total_revenue_year_to_date_value": 500.0,
    }
    snap = period_snapshot(row, "total_revenue")
    assert snap["current"] == 200.0
    assert snap["mom_pct"] == 100.0
    assert snap["yoy_pct"] == (200.0 - 150.0) / 150.0 * 100.0
    assert snap["rolling_3_month_average"] == 180.0
    assert snap["year_to_date_value"] == 500.0
