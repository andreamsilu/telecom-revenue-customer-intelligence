"""Unit tests for deterministic recommendation rules and engine."""

from __future__ import annotations

import pandas as pd
from src.recommendations.engine import generate_recommendations
from src.recommendations.rules import (
    rule_arpu_down_subscribers_up,
    rule_high_conversion_weak_retention,
    rule_negative_campaign_roi,
    rule_regional_subs_up_revenue_down,
)

REQUIRED_FIELDS = {
    "recommendation_id",
    "reporting_period",
    "module",
    "finding",
    "metric_name",
    "metric_value",
    "benchmark",
    "business_impact",
    "recommended_action",
    "priority",
    "responsible_department",
    "supporting_filters",
}


def test_arpu_down_subscribers_up_rule() -> None:
    frame = pd.DataFrame(
        {
            "reporting_month": ["2025-11-01", "2025-12-01"],
            "arpu": [50.0, 40.0],
            "total_subscribers": [100.0, 120.0],
            "total_revenue": [5000.0, 4800.0],
        }
    )
    recs = rule_arpu_down_subscribers_up(frame, "2025-12-01")
    assert len(recs) == 1
    payload = recs[0].as_dict()
    assert REQUIRED_FIELDS.issubset(payload.keys())
    assert recs[0].priority == "High"


def test_negative_campaign_roi_rule() -> None:
    campaigns = pd.DataFrame(
        {
            "campaign_id": ["CMP-A", "CMP-B"],
            "roi": [-0.5, 0.2],
            "conversion_rate": [0.1, 0.1],
            "conversions": [10, 10],
            "retained_after_30_days": [8, 8],
        }
    )
    recs = rule_negative_campaign_roi(campaigns, "2025-12-01")
    assert len(recs) == 1
    assert recs[0].recommendation_id.endswith("CMP-A")
    assert recs[0].metric_value < 0


def test_high_conversion_weak_retention_rule() -> None:
    campaigns = pd.DataFrame(
        {
            "campaign_id": ["CMP-WEAK"],
            "roi": [0.1],
            "conversion_rate": [0.12],
            "conversions": [100],
            "retained_after_30_days": [40],
        }
    )
    recs = rule_high_conversion_weak_retention(campaigns, "2025-12-01")
    assert len(recs) == 1
    assert "30 days" in recs[0].finding


def test_regional_subs_up_revenue_down() -> None:
    regional = pd.DataFrame(
        {
            "reporting_month": ["2025-12-01"],
            "region": ["Arusha"],
            "subscribers": [110.0],
            "subscribers_previous_month_value": [100.0],
            "total_revenue": [90.0],
            "total_revenue_previous_month_value": [100.0],
        }
    )
    recs = rule_regional_subs_up_revenue_down(regional, "2025-12-01")
    assert len(recs) == 1
    assert recs[0].supporting_filters["region"] == "Arusha"


def test_engine_is_deterministic_and_sorted() -> None:
    executive = pd.DataFrame(
        {
            "reporting_month": ["2025-11-01", "2025-12-01"],
            "arpu": [50.0, 40.0],
            "total_subscribers": [100.0, 120.0],
            "total_revenue": [5000.0, 4800.0],
        }
    )
    revenue = pd.DataFrame(
        {
            "reporting_month": ["2025-12-01"],
            "data_mb": [100.0],
            "data_mb_previous_month_value": [80.0],
            "arpu": [40.0],
            "arpu_previous_month_value": [50.0],
        }
    )
    subscriber = pd.DataFrame(
        {
            "reporting_month": [f"2025-{m:02d}-01" for m in range(9, 13)],
            "dormant_subscribers": [10, 12, 15, 20],
        }
    )
    churn = pd.DataFrame(
        {
            "reporting_month": ["2025-11-01", "2025-12-01"],
            "high_value_churned": [1, 5],
            "churn_rate": [0.1, 0.3],
            "churn_rate_rolling_3_month_average": [0.1, 0.15],
        }
    )
    recharge = pd.DataFrame(
        {
            "reporting_month": ["2025-12-01"],
            "recharge_frequency": [0.8],
            "recharge_frequency_previous_month_value": [1.0],
        }
    )
    regional = pd.DataFrame(
        {
            "reporting_month": ["2025-12-01"],
            "region": ["Geita"],
            "subscribers": [110.0],
            "subscribers_previous_month_value": [100.0],
            "total_revenue": [90.0],
            "total_revenue_previous_month_value": [100.0],
        }
    )
    campaigns = pd.DataFrame(
        {
            "campaign_id": ["CMP-NEG"],
            "roi": [-0.9],
            "conversion_rate": [0.05],
            "conversions": [10],
            "retained_after_30_days": [9],
        }
    )
    first = generate_recommendations(
        reporting_month="2025-12-01",
        executive_mart=executive,
        revenue_mart=revenue,
        subscriber_mart=subscriber,
        churn_mart=churn,
        recharge_mart=recharge,
        regional_mart=regional,
        campaign_mart=campaigns,
    )
    second = generate_recommendations(
        reporting_month="2025-12-01",
        executive_mart=executive,
        revenue_mart=revenue,
        subscriber_mart=subscriber,
        churn_mart=churn,
        recharge_mart=recharge,
        regional_mart=regional,
        campaign_mart=campaigns,
    )
    assert [r.recommendation_id for r in first] == [r.recommendation_id for r in second]
    assert len(first) >= 3
    priorities = [r.priority for r in first]
    order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    assert priorities == sorted(priorities, key=lambda p: order[p])
    for rec in first:
        assert REQUIRED_FIELDS.issubset(rec.as_dict().keys())
