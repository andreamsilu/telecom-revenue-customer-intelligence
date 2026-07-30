"""Streamlit entry point — UmojaTel executive intelligence shell."""

from __future__ import annotations

import streamlit as st
from app.components.filters import render_global_filters
from app.components.layout import (
    OPERATOR_NAME,
    PRODUCT_NAME,
    inject_theme_css,
    render_app_footer,
    render_empty_state,
    render_sidebar_brand,
    render_sidebar_footer,
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
    """Render the production application shell."""
    st.set_page_config(
        page_title=f"{OPERATOR_NAME} | {PRODUCT_NAME}",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_theme_css()
    settings = load_settings()
    profile = settings.profile_name

    render_sidebar_brand(
        reporting_month=settings.reporting_month.strftime("%Y-%m-%d")
    )
    page = st.sidebar.radio(
        "Workspace",
        list(PAGES.keys()),
        index=0,
        label_visibility="collapsed",
    )
    render_sidebar_footer()

    if not marts_available(profile):
        render_empty_state(
            "Analytical datasets are unavailable. Contact the analytics platform "
            "team or regenerate processed marts before continuing."
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
    render_app_footer()


if __name__ == "__main__":
    main()
