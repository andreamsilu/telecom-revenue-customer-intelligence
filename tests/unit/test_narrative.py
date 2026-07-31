"""Unit tests for executive month-story narratives."""

from __future__ import annotations

import pandas as pd
from src.analytics.narrative import build_month_story
from src.recommendations.models import Recommendation


def _executive_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "reporting_month": ["2025-11-01", "2025-12-01"],
            "total_revenue": [1000.0, 900.0],
            "arpu": [50.0, 40.0],
            "total_subscribers": [100.0, 120.0],
            "churn_rate": [3.0, 3.2],
        }
    )


def test_month_story_dilution_headline() -> None:
    story = build_month_story(_executive_frame(), "2025-12-01", [])
    assert "diluting monetisation" in story.headline
    assert len(story.movements) == 4
    assert story.priority_action is None
    assert story.closing  # always returns an interpreted close
    assert "Total revenue" in story.movements[0]


def test_month_story_uses_recommendation_drivers() -> None:
    rec = Recommendation(
        recommendation_id="REC-TEST",
        reporting_period="2025-12-01",
        module="Revenue Analytics",
        finding="ARPU fell while subscribers rose.",
        metric_name="ARPU",
        metric_value=40.0,
        benchmark=50.0,
        business_impact="Margin pressure from base dilution.",
        recommended_action="Upsell new acquisitions.",
        priority="High",
        responsible_department="Commercial",
    )
    story = build_month_story(_executive_frame(), "2025-12-01", [rec])
    assert story.drivers == ("ARPU fell while subscribers rose.",)
    assert story.priority_action == "Upsell new acquisitions."
    assert "Commercial" in story.closing
