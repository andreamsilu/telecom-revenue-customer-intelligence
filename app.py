"""Streamlit entry point for the Telecom Revenue & Customer Intelligence Platform."""

from __future__ import annotations

import streamlit as st
from app.components.filters import render_global_filters
from app.components.layout import inject_theme_css, render_empty_state
from app.pages.executive_overview import render_executive_overview
from app.services.data_loader import load_filter_options, marts_available
from src.config import load_settings

PAGES = ("Executive Overview",)


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

    st.sidebar.markdown(f"## {settings.project_name}")
    st.sidebar.caption(f"Profile: `{profile}` · Synthetic Tanzanian telecom data")
    page = st.sidebar.radio("Navigate", PAGES, index=0)

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

    if page == "Executive Overview":
        render_executive_overview(filters, options, profile_name=profile)


if __name__ == "__main__":
    main()
