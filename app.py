"""Streamlit entry point for the Telecom Revenue & Customer Intelligence Platform."""

from __future__ import annotations

import streamlit as st

from app.components.filters import render_global_filters
from app.components.layout import (
    inject_theme_css,
    render_empty_state,
    render_sidebar_brand,
)
from app.pages.campaign_analytics import render_campaign_analytics
from app.pages.churn_retention import render_churn_retention
from app.pages.executive_overview import render_executive_overview
from app.pages.executive_recommendations import render_executive_recommendations
from app.pages.mobile_money_analytics import render_mobile_money_analytics
from app.pages.recharge_analytics import render_recharge_analytics
from app.pages.regional_performance import render_regional_performance
from app.pages.revenue_analytics import render_revenue_analytics
from app.pages.subscriber_analytics import render_subscriber_analytics
from app.services.data_loader import load_filter_options, marts_available
from src.config import load_settings

PAGES = {
    "Executive Overview": render_executive_overview,
    "Subscriber Analytics": render_subscriber_analytics,
    "Revenue Analytics": render_revenue_analytics,
    "Churn and Retention": render_churn_retention,
    "Recharge Analytics": render_recharge_analytics,
    "Mobile Money Analytics": render_mobile_money_analytics,
    "Campaign Analytics": render_campaign_analytics,
    "Regional Performance": render_regional_performance,
    "Executive Recommendations": render_executive_recommendations,
}


def main() -> None:
    """Render the application shell, global filters, and active page."""
    st.set_page_config(
        page_title="Telecom Revenue & Customer Intelligence",
        page_icon="📡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_theme_css()
    settings = load_settings()
    profile = settings.profile_name

    render_sidebar_brand(project_name=settings.project_name, profile=profile)
    page = st.sidebar.radio(
        "Page",
        list(PAGES.keys()),
        index=0,
        label_visibility="collapsed",
    )
    st.sidebar.divider()
    st.sidebar.caption("Filters are at the top of each page.")

    if not marts_available(profile):
        render_empty_state(
            "Processed marts were not found in this environment. "
            "Locally, run `python -m scripts.run_pipeline --profile development` "
            "then reload. On Streamlit Community Cloud, ensure the committed "
            "dashboard marts under `data/processed/` are present on `main`."
        )
        return

    try:
        options = load_filter_options(profile)
    except FileNotFoundError as exc:
        render_empty_state(str(exc))
        return

    filters = render_global_filters(
        settings,
        available_months=options.months,
        regions=options.regions,
        segments=options.segments,
        account_types=options.account_types,
        product_categories=options.product_categories,
    )

    PAGES[page](filters, options, profile_name=profile)


if __name__ == "__main__":
    main()
