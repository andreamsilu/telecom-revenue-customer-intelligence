"""Unit tests for domain KPI services."""

from __future__ import annotations

import pandas as pd
import pytest
from src.analytics.campaign_regional import campaign_kpi_summary, regional_kpi_cards
from src.analytics.domain import (
    mobile_money_kpi_cards,
    recharge_kpi_cards,
    retention_kpi_cards,
    subscriber_kpi_cards,
)
from src.analytics.executive import executive_kpi_cards, revenue_kpi_cards


def _executive_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "reporting_month": ["2025-11-01", "2025-12-01"],
            "total_revenue": [1000.0, 1100.0],
            "total_revenue_previous_month_value": [900.0, 1000.0],
            "arpu": [50.0, 45.0],
            "total_subscribers": [100.0, 110.0],
            "active_subscribers": [80.0, 88.0],
            "churn_rate": [0.20, 0.15],
        }
    )


def test_executive_kpi_cards_mom_and_pp() -> None:
    cards = {c.name: c for c in executive_kpi_cards(_executive_frame(), "2025-12-01")}
    assert cards["Total Revenue"].comparison_value == 10.0
    assert cards["Total Revenue"].comparison_method == "pct"
    assert cards["ARPU"].comparison_value == -10.0
    assert cards["Churn Rate"].comparison_method == "pp"
    assert cards["Churn Rate"].comparison_value == pytest.approx(-0.05)


def test_revenue_kpi_includes_yoy_rolling_ytd() -> None:
    frame = pd.DataFrame(
        {
            "reporting_month": ["2025-12-01"],
            "total_revenue": [200.0],
            "total_revenue_previous_month_value": [100.0],
            "total_revenue_prior_year_value": [160.0],
            "total_revenue_rolling_3_month_average": [180.0],
            "total_revenue_year_to_date_value": [2000.0],
            "data_mb": [10.0],
            "data_mb_previous_month_value": [8.0],
            "recharge_value": [50.0],
            "recharge_value_previous_month_value": [40.0],
        }
    )
    cards = {c.name: c for c in revenue_kpi_cards(frame, "2025-12-01")}
    assert cards["Total Revenue YoY"].comparison_label == "YoY"
    assert cards["Rolling 3-Month Revenue Avg"].value == 180.0
    assert cards["YTD Revenue"].value == 2000.0


def test_subscriber_active_rate_uses_percentage_points() -> None:
    frame = pd.DataFrame(
        {
            "reporting_month": ["2025-12-01"],
            "total_subscribers": [100.0],
            "total_subscribers_previous_month_value": [90.0],
            "active_rate": [0.80],
            "active_rate_previous_month_value": [0.85],
            "new_subscribers": [5.0],
            "new_subscribers_previous_month_value": [4.0],
        }
    )
    cards = {c.name: c for c in subscriber_kpi_cards(frame, "2025-12-01")}
    assert cards["Active Rate"].value == 80.0
    assert cards["Active Rate"].comparison_method == "pp"
    assert cards["Active Rate"].comparison_value == -5.0


def test_retention_churn_rate_uses_pp() -> None:
    frame = pd.DataFrame(
        {
            "reporting_month": ["2025-11-01", "2025-12-01"],
            "churn_rate": [0.20, 0.15],
            "churn_rate_previous_month_value": [0.25, 0.20],
            "revenue_lost_to_churn": [100.0, 80.0],
            "revenue_lost_to_churn_previous_month_value": [90.0, 100.0],
            "high_value_churned": [2, 3],
        }
    )
    cards = {c.name: c for c in retention_kpi_cards(frame, "2025-12-01")}
    assert cards["Churn Rate"].comparison_method == "pp"
    assert cards["Churn Rate"].comparison_value == pytest.approx(-0.05)


def test_recharge_and_mm_kpis() -> None:
    recharge = pd.DataFrame(
        {
            "reporting_month": ["2025-12-01"],
            "recharge_frequency": [1.2],
            "recharge_frequency_previous_month_value": [1.0],
            "average_recharge_value": [5000.0],
            "average_recharge_value_previous_month_value": [4000.0],
            "total_recharge_value": [100000.0],
            "total_recharge_value_previous_month_value": [80000.0],
        }
    )
    mm = pd.DataFrame(
        {
            "reporting_month": ["2025-12-01"],
            "active_users": [50.0],
            "active_users_previous_month_value": [40.0],
            "fee_revenue": [1000.0],
            "fee_revenue_previous_month_value": [800.0],
            "failed_transaction_rate": [0.10],
            "failed_transaction_rate_previous_month_value": [0.08],
        }
    )
    r_cards = {c.name: c for c in recharge_kpi_cards(recharge, "2025-12-01")}
    m_cards = {c.name: c for c in mobile_money_kpi_cards(mm, "2025-12-01")}
    assert r_cards["Recharge Frequency"].comparison_value == pytest.approx(20.0)
    assert m_cards["Failed Transaction Rate"].comparison_method == "pp"
    assert m_cards["Failed Transaction Rate"].comparison_value == pytest.approx(2.0)


def test_campaign_and_regional_kpis() -> None:
    campaigns = pd.DataFrame(
        {
            "customers_contacted": [100, 50],
            "conversions": [10, 5],
            "revenue_generated": [1000.0, 500.0],
            "campaign_cost": [200.0, 100.0],
        }
    )
    summary = {c.name: c for c in campaign_kpi_summary(campaigns)}
    assert summary["Campaign Portfolio ROI"].value == ((1500 - 300) / 300) * 100
    regional = pd.DataFrame(
        {
            "reporting_month": ["2025-12-01", "2025-12-01"],
            "region": ["Dar es Salaam", "Geita"],
            "total_revenue": [200.0, 50.0],
            "total_revenue_previous_month_value": [100.0, 60.0],
        }
    )
    cards = regional_kpi_cards(regional, "2025-12-01")
    assert "Dar es Salaam" in cards[0].name
    assert cards[0].comparison_value == 100.0
