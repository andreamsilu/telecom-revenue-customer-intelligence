"""Customer event stream generation from transactions and lifecycle changes."""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd

from src.config.settings import AppSettings
from src.utils.logging import get_logger

logger = get_logger(__name__)


def generate_customer_events(
    settings: AppSettings,
    customers: pd.DataFrame,
    recharges: pd.DataFrame,
    mobile_money: pd.DataFrame,
    snapshot: pd.DataFrame,
    *,
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    """Generate customer events from source activity and lifecycle transitions."""
    base_rng = rng or np.random.default_rng(settings.random_seed + 505)
    frames: list[pd.DataFrame] = []

    cust = customers[
        ["customer_id", "registration_date", "region", "acquisition_channel"]
    ].copy()
    cust["registration_date"] = pd.to_datetime(cust["registration_date"])

    reg = pd.DataFrame(
        {
            "customer_id": cust["customer_id"],
            "event_timestamp": cust["registration_date"].dt.strftime(
                "%Y-%m-%d 09:00:00"
            ),
            "event_type": "SIM Registration",
            "event_channel": cust["acquisition_channel"].astype(str),
            "region": cust["region"],
            "related_transaction_id": None,
            "event_value": np.nan,
        }
    )
    frames.append(reg)

    if not recharges.empty:
        rec = pd.DataFrame(
            {
                "customer_id": recharges["customer_id"],
                "event_timestamp": recharges["recharge_timestamp"].astype(str),
                "event_type": np.where(
                    recharges["recharge_type"].astype(str) == "airtime",
                    "Airtime Recharge",
                    "Bundle Purchase",
                ),
                "event_channel": recharges["recharge_channel"].astype(str),
                "region": recharges["region"],
                "related_transaction_id": recharges["recharge_id"],
                "event_value": recharges["amount"].astype(float),
            }
        )
        frames.append(rec)

    mm_ok = mobile_money[mobile_money["transaction_status"] == "Successful"]
    if not mm_ok.empty:
        mm = pd.DataFrame(
            {
                "customer_id": mm_ok["customer_id"],
                "event_timestamp": mm_ok["transaction_timestamp"].astype(str),
                "event_type": "Mobile Money Usage",
                "event_channel": mm_ok["channel"].astype(str),
                "region": mm_ok["origin_region"],
                "related_transaction_id": mm_ok["transaction_id"],
                "event_value": mm_ok["amount"].astype(float),
            }
        )
        frames.append(mm)

    region_map = cust.set_index("customer_id")["region"].to_dict()

    churned = snapshot.loc[snapshot["newly_churned"]].copy()
    if not churned.empty:
        month = pd.to_datetime(churned["reporting_month"])
        # Use month-end timestamp for churn classification events.
        churn_ts = (month + pd.offsets.MonthEnd(0)).dt.strftime("%Y-%m-%d 23:00:00")
        frames.append(
            pd.DataFrame(
                {
                    "customer_id": churned["customer_id"],
                    "event_timestamp": churn_ts,
                    "event_type": "Churn",
                    "event_channel": "System",
                    "region": churned["customer_id"].map(region_map),
                    "related_transaction_id": None,
                    "event_value": churned["monthly_revenue"].astype(float),
                }
            )
        )

    reactivated = snapshot.loc[snapshot["newly_reactivated"]].copy()
    if not reactivated.empty:
        last = pd.to_datetime(
            reactivated["last_activity_date"].fillna(reactivated["reporting_month"])
        )
        frames.append(
            pd.DataFrame(
                {
                    "customer_id": reactivated["customer_id"],
                    "event_timestamp": last.dt.strftime("%Y-%m-%d 12:00:00"),
                    "event_type": "Reactivation",
                    "event_channel": "System",
                    "region": reactivated["customer_id"].map(region_map),
                    "related_transaction_id": None,
                    "event_value": reactivated["monthly_revenue"].astype(float),
                }
            )
        )

    sample_n = max(1, int(0.04 * len(cust)))
    sampled = cust.sample(
        n=min(sample_n, len(cust)),
        random_state=int(base_rng.integers(0, 1_000_000_000)),
    )
    noise_rows: list[dict[str, object]] = []
    for customer in sampled.itertuples(index=False):
        day_offset = int(base_rng.integers(0, 700))
        ts = pd.Timestamp(settings.start_date) + pd.Timedelta(days=day_offset)
        if ts.date() > settings.end_date:
            continue
        event_type = "Complaint" if base_rng.random() < 0.6 else "SIM Swap"
        noise_rows.append(
            {
                "customer_id": customer.customer_id,
                "event_timestamp": datetime(
                    ts.year, ts.month, ts.day, int(base_rng.integers(8, 20)), 0, 0
                ).isoformat(sep=" "),
                "event_type": event_type,
                "event_channel": (
                    "Call Centre" if event_type == "Complaint" else "Dealer"
                ),
                "region": customer.region,
                "related_transaction_id": None,
                "event_value": np.nan,
            }
        )
    if noise_rows:
        frames.append(pd.DataFrame(noise_rows))

    frame = pd.concat(frames, ignore_index=True)
    frame.insert(0, "event_id", [f"EVT-{i + 1:010d}" for i in range(len(frame))])
    logger.info("Built customer_events (%s rows)", f"{len(frame):,}")
    return frame
