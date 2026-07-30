"""Smoke tests for Streamlit page module wiring."""

from __future__ import annotations

from app.pages import (
    campaign_analytics,
    churn_retention,
    executive_overview,
    executive_recommendations,
    mobile_money_analytics,
    recharge_analytics,
    regional_performance,
    revenue_analytics,
    subscriber_analytics,
)


def test_all_dashboard_page_renderers_exist() -> None:
    """Nine Version-1 analytical pages expose callable render functions."""
    renderers = [
        executive_overview.render_executive_overview,
        subscriber_analytics.render_subscriber_analytics,
        revenue_analytics.render_revenue_analytics,
        churn_retention.render_churn_retention,
        recharge_analytics.render_recharge_analytics,
        mobile_money_analytics.render_mobile_money_analytics,
        campaign_analytics.render_campaign_analytics,
        regional_performance.render_regional_performance,
        executive_recommendations.render_executive_recommendations,
    ]
    assert len(renderers) == 9
    assert all(callable(fn) for fn in renderers)
