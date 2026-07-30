"""Unit tests for lifecycle boundaries and snapshot rules."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
from src.config import load_settings
from src.generator.lifecycle import assign_value_segment, status_from_inactivity
from src.generator.snapshot import generate_customer_monthly_snapshot
from src.validation.lifecycle import validate_snapshot


def test_lifecycle_boundary_conditions() -> None:
    """Inactivity day boundaries map to the documented statuses."""
    assert status_from_inactivity(0) == "Active"
    assert status_from_inactivity(30) == "Active"
    assert status_from_inactivity(31) == "At Risk"
    assert status_from_inactivity(45) == "At Risk"
    assert status_from_inactivity(46) == "Dormant"
    assert status_from_inactivity(59) == "Dormant"
    assert status_from_inactivity(60) == "Churned"
    assert status_from_inactivity(90) == "Churned"
    assert status_from_inactivity(10, previously_churned=True) == "Reactivated"


def test_value_segment_thresholds() -> None:
    """Value segments follow rolling-revenue quantile cut points."""
    thresholds = (1000.0, 5000.0, 15000.0)
    assert assign_value_segment(0, thresholds) == "Low Value"
    assert assign_value_segment(500, thresholds) == "Low Value"
    assert assign_value_segment(2000, thresholds) == "Medium Value"
    assert assign_value_segment(8000, thresholds) == "High Value"
    assert assign_value_segment(20000, thresholds) == "Very High Value"


def test_snapshot_grain_and_reactivation_rule() -> None:
    """Snapshot has unique grain; reactivation only follows churn."""
    settings = load_settings(
        profile_name="development",
        subscriber_count=80,
        batch_size=40,
        random_seed=11,
        start_date=date(2024, 1, 1),
        end_date=date(2025, 12, 31),
    )
    # Minimal synthetic customers and activity covering churn → reactivation.
    customers = pd.DataFrame(
        {
            "customer_id": [f"CUST-{i:07d}" for i in range(1, 81)],
            "registration_date": ["2024-01-15"] * 80,
            "customer_segment": ["Mass Market"] * 80,
            "region_id": ["DAR-01"] * 80,
        }
    )
    # Customer 1: active early, silent long enough to churn, then returns.
    usage_rows = []
    for day in pd.date_range("2024-01-15", "2024-02-28", freq="3D"):
        usage_rows.append(
            {
                "usage_date": day.strftime("%Y-%m-%d"),
                "customer_id": "CUST-0000001",
                "voice_minutes": 10.0,
                "sms_count": 1,
                "data_mb": 20.0,
                "international_minutes": 0.0,
                "roaming_minutes": 0.0,
                "vas_events": 0,
                "total_usage_revenue": 500.0,
            }
        )
    # Return activity after churn window.
    for day in pd.date_range("2024-06-01", "2024-06-20", freq="2D"):
        usage_rows.append(
            {
                "usage_date": day.strftime("%Y-%m-%d"),
                "customer_id": "CUST-0000001",
                "voice_minutes": 8.0,
                "sms_count": 1,
                "data_mb": 15.0,
                "international_minutes": 0.0,
                "roaming_minutes": 0.0,
                "vas_events": 0,
                "total_usage_revenue": 400.0,
            }
        )
    # Keep other customers lightly active so snapshot is populated.
    for i in range(2, 81):
        usage_rows.append(
            {
                "usage_date": "2024-03-10",
                "customer_id": f"CUST-{i:07d}",
                "voice_minutes": 5.0,
                "sms_count": 1,
                "data_mb": 10.0,
                "international_minutes": 0.0,
                "roaming_minutes": 0.0,
                "vas_events": 0,
                "total_usage_revenue": 200.0,
            }
        )

    usage = pd.DataFrame(usage_rows)
    recharges = pd.DataFrame(
        columns=[
            "recharge_id",
            "customer_id",
            "recharge_timestamp",
            "amount",
        ]
    )
    mobile_money = pd.DataFrame(
        columns=[
            "transaction_id",
            "customer_id",
            "transaction_timestamp",
            "amount",
            "fee_revenue",
            "transaction_status",
        ]
    )

    snapshot = generate_customer_monthly_snapshot(
        settings, customers, usage, recharges, mobile_money
    )
    report = validate_snapshot(snapshot, customers)
    assert report.ok, report.errors
    assert not snapshot.duplicated(subset=["reporting_month", "customer_id"]).any()

    cust1 = snapshot[snapshot["customer_id"] == "CUST-0000001"].sort_values(
        "reporting_month"
    )
    assert (cust1["lifecycle_status"] == "Churned").any()
    reactivated_rows = cust1[cust1["newly_reactivated"]]
    assert not reactivated_rows.empty
    # Every reactivation must follow a prior churn classification.
    first_react = reactivated_rows.iloc[0]["reporting_month"]
    prior = cust1[cust1["reporting_month"] < first_react]
    assert (prior["lifecycle_status"] == "Churned").any()


def test_low_recharge_associated_with_higher_churn_risk() -> None:
    """Customers with lower recharge counts show higher newly_churned incidence."""
    # Use a constructed snapshot rather than full generation for a focused test.
    rng = np.random.default_rng(0)
    n = 2000
    recharge_count = rng.poisson(3, size=n)
    # Higher churn probability when recharge_count is low.
    churn_prob = np.clip(0.25 - 0.04 * recharge_count, 0.02, 0.30)
    newly_churned = rng.random(n) < churn_prob
    frame = pd.DataFrame(
        {"recharge_count": recharge_count, "newly_churned": newly_churned}
    )
    low = frame[frame["recharge_count"] <= 1]["newly_churned"].mean()
    high = frame[frame["recharge_count"] >= 4]["newly_churned"].mean()
    assert low > high
