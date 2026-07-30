"""Streamlit entry point for the Telecom Revenue & Customer Intelligence Platform.

Phase 1: placeholder only. Analytical pages are added in later phases.
"""

from __future__ import annotations

import streamlit as st


def main() -> None:
    """Render the Phase 1 placeholder application shell."""
    st.set_page_config(
        page_title="Telecom Revenue & Customer Intelligence",
        page_icon="📡",
        layout="wide",
    )
    st.title("Telecom Revenue & Customer Intelligence Platform")
    st.caption(
        "A Python-Based Executive Decision Support Platform "
        "for Telecommunications Operators in Tanzania."
    )
    st.info(
        "Phase 1 scaffolding is complete. Analytical dashboard pages "
        "will be added in later phases. All data in this project is synthetic."
    )
    st.markdown(
        """
        **Current status:** Project scaffolding, configuration, documentation,
        and health-check tooling.

        **Next:** Reference datasets and customer master-data generation (Phase 2).
        """
    )


if __name__ == "__main__":
    main()
