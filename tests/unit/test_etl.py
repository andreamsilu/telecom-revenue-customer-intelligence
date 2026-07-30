"""Unit tests for ETL comparisons and mart construction."""

from __future__ import annotations

import pandas as pd
from src.config import load_settings
from src.etl.comparisons import add_monthly_comparisons
from src.etl.dimensions import build_dim_date, build_dim_product
from src.etl.marts import build_revenue_monthly_mart, build_subscriber_monthly_mart
from src.etl.marts_extra import build_campaign_performance_mart
from src.generator import generate_campaigns, generate_products
from src.generator.calendar import generate_calendar


def test_add_monthly_comparisons_columns() -> None:
    """Comparison helper adds MoM/YoY/rolling/YTD fields."""
    frame = pd.DataFrame(
        {
            "reporting_month": [f"2024-{m:02d}-01" for m in range(1, 13)]
            + [f"2025-{m:02d}-01" for m in range(1, 13)],
            "total_revenue": list(range(24)),
        }
    )
    out = add_monthly_comparisons(
        frame, month_col="reporting_month", value_cols=["total_revenue"]
    )
    assert "total_revenue_previous_month_value" in out.columns
    assert "total_revenue_month_over_month_change" in out.columns
    assert "total_revenue_prior_year_value" in out.columns
    assert "total_revenue_year_over_year_change" in out.columns
    assert "total_revenue_rolling_3_month_average" in out.columns
    assert "total_revenue_rolling_12_month_value" in out.columns
    assert "total_revenue_year_to_date_value" in out.columns
    jan_2025 = out[out["reporting_month"] == "2025-01-01"].iloc[0]
    assert jan_2025["total_revenue_prior_year_value"] == 0


def test_dimension_keys_unique() -> None:
    """Date and product dimensions enforce unique keys."""
    settings = load_settings(profile_name="development")
    dim_date = build_dim_date(generate_calendar(settings))
    dim_product = build_dim_product(generate_products(settings))
    assert dim_date["date_key"].is_unique
    assert dim_product["product_id"].is_unique
    assert len(dim_date) == 731


def test_revenue_mart_reconciles_to_snapshot() -> None:
    """Revenue mart totals match snapshot sums."""
    snapshot = pd.DataFrame(
        {
            "reporting_month": ["2025-01-01"] * 3 + ["2025-02-01"] * 2,
            "customer_id": ["A", "B", "C", "A", "B"],
            "monthly_revenue": [10.0, 20.0, 30.0, 40.0, 50.0],
            "monthly_voice_minutes": [1, 1, 1, 1, 1],
            "monthly_sms_count": [1, 1, 1, 1, 1],
            "monthly_data_mb": [1, 1, 1, 1, 1],
            "recharge_value": [0, 0, 0, 0, 0],
            "mobile_money_transaction_value": [0, 0, 0, 0, 0],
            "lifecycle_status": ["Active"] * 5,
            "newly_registered": [False] * 5,
        }
    )
    mart = build_revenue_monthly_mart(snapshot)
    assert (
        float(
            mart.loc[mart["reporting_month"] == "2025-01-01", "total_revenue"].iloc[0]
        )
        == 60.0
    )
    assert (
        float(
            mart.loc[mart["reporting_month"] == "2025-02-01", "total_revenue"].iloc[0]
        )
        == 90.0
    )
    sub = build_subscriber_monthly_mart(snapshot)
    assert (
        int(
            sub.loc[sub["reporting_month"] == "2025-01-01", "total_subscribers"].iloc[0]
        )
        == 3
    )


def test_campaign_performance_rates() -> None:
    """Campaign mart computes response/conversion/ROI fields."""
    settings = load_settings(profile_name="development")
    campaigns = generate_campaigns(settings)
    responses = pd.DataFrame(
        {
            "campaign_id": [campaigns.iloc[0]["campaign_id"]] * 10,
            "contacted": [True] * 10,
            "responded": [True] * 5 + [False] * 5,
            "converted": [True] * 2 + [False] * 8,
            "revenue_generated": [1000.0] * 2 + [0.0] * 8,
            "retained_after_30_days": [True] * 2 + [False] * 8,
            "churned_after_campaign": [False] * 10,
        }
    )
    mart = build_campaign_performance_mart(campaigns, responses)
    row = mart[mart["campaign_id"] == campaigns.iloc[0]["campaign_id"]].iloc[0]
    assert abs(float(row["response_rate"]) - 0.5) < 1e-9
    assert abs(float(row["conversion_rate"]) - 0.2) < 1e-9
    assert "roi" in mart.columns
