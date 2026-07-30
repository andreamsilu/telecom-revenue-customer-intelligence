"""Monthly customer lifecycle snapshot generation."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from src.config.settings import AppSettings
from src.generator.activity import (
    apply_attrition_cutoff,
    build_qualifying_activity,
    select_attrition_cutoffs,
)
from src.generator.lifecycle import assign_value_segment, status_from_inactivity
from src.utils.logging import get_logger

logger = get_logger(__name__)


def _month_starts(start: date, end: date) -> list[date]:
    """Return first day of each month in the inclusive period."""
    months: list[date] = []
    current = start.replace(day=1)
    last = end.replace(day=1)
    while current <= last:
        months.append(current)
        year = current.year + (1 if current.month == 12 else 0)
        month = 1 if current.month == 12 else current.month + 1
        current = date(year, month, 1)
    return months


def _month_end(month_start: date, period_end: date) -> date:
    """Return last day of month clipped to period end."""
    if month_start.month == 12:
        nxt = date(month_start.year + 1, 1, 1)
    else:
        nxt = date(month_start.year, month_start.month + 1, 1)
    return min(nxt - timedelta(days=1), period_end)


def generate_customer_monthly_snapshot(
    settings: AppSettings,
    customers: pd.DataFrame,
    usage: pd.DataFrame,
    recharges: pd.DataFrame,
    mobile_money: pd.DataFrame,
) -> pd.DataFrame:
    """Build one lifecycle snapshot row per customer per reporting month.

    Lifecycle status is derived from qualifying activity after applying a
    deterministic engagement-attrition mask (low-recharge customers are more
    likely to stop), so churn and reactivation emerge naturally.
    """
    cutoffs, returns = select_attrition_cutoffs(
        customers,
        recharges,
        seed=settings.random_seed,
    )
    usage = apply_attrition_cutoff(
        usage,
        cutoffs,
        returns,
        customer_col="customer_id",
        timestamp_col="usage_date",
    )
    recharges = apply_attrition_cutoff(
        recharges,
        cutoffs,
        returns,
        customer_col="customer_id",
        timestamp_col="recharge_timestamp",
    )
    mobile_money = apply_attrition_cutoff(
        mobile_money,
        cutoffs,
        returns,
        customer_col="customer_id",
        timestamp_col="transaction_timestamp",
    )

    activity = build_qualifying_activity(usage, recharges, mobile_money)
    cust = customers[["customer_id", "registration_date", "customer_segment"]].copy()
    cust["customer_id"] = cust["customer_id"].astype(str)
    cust["registration_date"] = pd.to_datetime(cust["registration_date"]).dt.date

    usage = usage.copy()
    usage["customer_id"] = usage["customer_id"].astype(str)
    usage["usage_date"] = pd.to_datetime(usage["usage_date"])
    usage["month_start"] = usage["usage_date"].dt.to_period("M").dt.to_timestamp()

    recharges = recharges.copy()
    recharges["customer_id"] = recharges["customer_id"].astype(str)
    recharges["recharge_timestamp"] = pd.to_datetime(recharges["recharge_timestamp"])
    recharges["month_start"] = (
        recharges["recharge_timestamp"].dt.to_period("M").dt.to_timestamp()
    )

    mobile_money = mobile_money.copy()
    mobile_money["customer_id"] = mobile_money["customer_id"].astype(str)
    mobile_money["transaction_timestamp"] = pd.to_datetime(
        mobile_money["transaction_timestamp"]
    )
    mobile_money["month_start"] = (
        mobile_money["transaction_timestamp"].dt.to_period("M").dt.to_timestamp()
    )
    mm_success = mobile_money[mobile_money["transaction_status"] == "Successful"]

    if usage.empty:
        usage_monthly = pd.DataFrame(
            columns=[
                "customer_id",
                "month_start",
                "monthly_voice_minutes",
                "monthly_sms_count",
                "monthly_data_mb",
                "monthly_usage_revenue",
            ]
        )
    else:
        usage_monthly = usage.groupby(
            ["customer_id", "month_start"], as_index=False
        ).agg(
            monthly_voice_minutes=("voice_minutes", "sum"),
            monthly_sms_count=("sms_count", "sum"),
            monthly_data_mb=("data_mb", "sum"),
            monthly_usage_revenue=("total_usage_revenue", "sum"),
        )

    if recharges.empty:
        recharge_monthly = pd.DataFrame(
            columns=[
                "customer_id",
                "month_start",
                "recharge_count",
                "recharge_value",
            ]
        )
    else:
        recharge_monthly = recharges.groupby(
            ["customer_id", "month_start"], as_index=False
        ).agg(
            recharge_count=("recharge_id", "count"),
            recharge_value=("amount", "sum"),
        )

    if mm_success.empty:
        mm_monthly = pd.DataFrame(
            columns=[
                "customer_id",
                "month_start",
                "mobile_money_transaction_value",
                "mobile_money_fee_revenue",
                "mm_txn_count",
            ]
        )
    else:
        mm_monthly = mm_success.groupby(
            ["customer_id", "month_start"], as_index=False
        ).agg(
            mobile_money_transaction_value=("amount", "sum"),
            mobile_money_fee_revenue=("fee_revenue", "sum"),
            mm_txn_count=("transaction_id", "count"),
        )

    # Precompute last activity as-of each month-end using merge_asof style.
    activity = activity.copy()
    activity["activity_date"] = pd.to_datetime(activity["activity_date"])

    ever_churned: dict[str, bool] = {cid: False for cid in cust["customer_id"].tolist()}
    previous_status: dict[str, str | None] = {
        cid: None for cid in cust["customer_id"].tolist()
    }
    revenue_history: dict[str, list[float]] = {
        cid: [] for cid in cust["customer_id"].tolist()
    }

    snapshot_rows: list[dict[str, object]] = []
    months = _month_starts(settings.start_date, settings.end_date)

    for month_start in months:
        month_end = _month_end(month_start, settings.end_date)
        month_ts = pd.Timestamp(month_start)
        month_end_ts = pd.Timestamp(month_end)
        logger.info("Building lifecycle snapshot for %s", month_start.isoformat())

        eligible = cust[cust["registration_date"] <= month_end].copy()
        if eligible.empty:
            continue

        # Last activity on or before month-end.
        act_cut = activity[activity["activity_date"] <= month_end_ts]
        last_activity = act_cut.groupby("customer_id", as_index=True)[
            "activity_date"
        ].max()

        u = usage_monthly[usage_monthly["month_start"] == month_ts]
        r = recharge_monthly[recharge_monthly["month_start"] == month_ts]
        m = mm_monthly[mm_monthly["month_start"] == month_ts]

        metrics = (
            eligible[["customer_id", "registration_date"]]
            .merge(u, on="customer_id", how="left")
            .merge(r, on="customer_id", how="left")
            .merge(m, on="customer_id", how="left")
        )
        for col in (
            "monthly_voice_minutes",
            "monthly_sms_count",
            "monthly_data_mb",
            "monthly_usage_revenue",
            "recharge_count",
            "recharge_value",
            "mobile_money_transaction_value",
            "mobile_money_fee_revenue",
            "mm_txn_count",
        ):
            metrics[col] = pd.to_numeric(metrics[col], errors="coerce").fillna(0.0)

        metrics["monthly_revenue"] = (
            metrics["monthly_usage_revenue"]
            + metrics["recharge_value"]
            + metrics["mobile_money_fee_revenue"]
        )

        month_rows: list[dict[str, object]] = []
        rolling_values: list[float] = []

        for record in metrics.to_dict(orient="records"):
            cid = str(record["customer_id"])
            reg_date = record["registration_date"]
            if not isinstance(reg_date, date):
                reg_date = pd.Timestamp(str(reg_date)).date()

            last = last_activity.get(cid)
            if pd.isna(last):
                inactivity = (month_end - reg_date).days
                last_activity_out: date | None = None
            else:
                last_date = pd.Timestamp(last).date()
                inactivity = (month_end - last_date).days
                last_activity_out = last_date

            prev = previous_status[cid]
            was_churned = ever_churned[cid]
            if was_churned and inactivity <= 30:
                status = "Reactivated"
            else:
                status = status_from_inactivity(int(inactivity))

            if status == "Churned":
                ever_churned[cid] = True

            newly_registered = (
                reg_date.year == month_start.year
                and reg_date.month == month_start.month
            )
            newly_churned = status == "Churned" and prev != "Churned"
            newly_reactivated = status == "Reactivated" and prev == "Churned"

            monthly_revenue = float(record["monthly_revenue"])
            hist = revenue_history[cid]
            hist.append(monthly_revenue)
            rolling_3 = float(sum(hist[-3:]))
            revenue_history[cid] = hist
            rolling_values.append(rolling_3)

            tenure_months = (month_start.year - reg_date.year) * 12 + (
                month_start.month - reg_date.month
            )

            month_rows.append(
                {
                    "reporting_month": month_start.isoformat(),
                    "customer_id": cid,
                    "lifecycle_status": status,
                    "last_activity_date": (
                        last_activity_out.isoformat() if last_activity_out else None
                    ),
                    "inactivity_days": int(inactivity),
                    "monthly_revenue": round(monthly_revenue, 2),
                    "rolling_3_month_revenue": round(rolling_3, 2),
                    "monthly_voice_minutes": round(
                        float(record["monthly_voice_minutes"]), 2
                    ),
                    "monthly_sms_count": int(record["monthly_sms_count"]),
                    "monthly_data_mb": round(float(record["monthly_data_mb"]), 2),
                    "recharge_count": int(record["recharge_count"]),
                    "recharge_value": round(float(record["recharge_value"]), 2),
                    "mobile_money_active": bool(float(record["mm_txn_count"]) > 0),
                    "mobile_money_transaction_value": round(
                        float(record["mobile_money_transaction_value"]), 2
                    ),
                    "newly_registered": bool(newly_registered),
                    "newly_churned": bool(newly_churned),
                    "newly_reactivated": bool(newly_reactivated),
                    "tenure_months": int(max(tenure_months, 0)),
                    "value_segment": "Low Value",
                }
            )
            previous_status[cid] = status

        # Value segments from within-month rolling revenue distribution.
        positive = np.array([v for v in rolling_values if v > 0], dtype=float)
        if positive.size >= 4:
            thresholds = (
                float(np.quantile(positive, 0.50)),
                float(np.quantile(positive, 0.75)),
                float(np.quantile(positive, 0.90)),
            )
        else:
            thresholds = (1_000.0, 5_000.0, 15_000.0)

        for row_dict in month_rows:
            row_dict["value_segment"] = assign_value_segment(
                float(str(row_dict["rolling_3_month_revenue"])),
                thresholds,
            )
            snapshot_rows.append(row_dict)

    frame = pd.DataFrame(snapshot_rows)
    if frame.empty:
        return frame

    dupes = frame.duplicated(subset=["reporting_month", "customer_id"]).sum()
    if dupes:
        raise ValueError(f"Snapshot grain violated: {dupes} duplicate keys.")
    logger.info("Built customer_monthly_snapshot (%s rows)", f"{len(frame):,}")
    return frame
