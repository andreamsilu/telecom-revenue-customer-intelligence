"""Deterministic recommendation rule functions.

Each rule returns zero or more ``Recommendation`` objects supported by metrics.
"""

from __future__ import annotations

import pandas as pd

from src.analytics.comparisons import percent_change, safe_float
from src.analytics.helpers import optional_float
from src.analytics.loaders import row_for_month
from src.recommendations.models import Recommendation

# Conversion "high" threshold and retention-after-conversion "weak" threshold.
HIGH_CONVERSION_RATE = 0.08
WEAK_RETENTION_RATIO = 0.55
# ARPU considered "flat" when |MoM %| is below this band.
ARPU_FLAT_BAND_PCT = 1.0
# Dormant streak length (consecutive MoM increases).
DORMANT_STREAK_MONTHS = 3


def rule_arpu_down_subscribers_up(
    executive_mart: pd.DataFrame,
    reporting_month: str,
) -> list[Recommendation]:
    """Flag ARPU decline concurrent with subscriber growth."""
    row = row_for_month(executive_mart, reporting_month)
    month = str(row["reporting_month"])
    prev = _previous_row(executive_mart, month)
    if prev is None:
        return []
    arpu = safe_float(row["arpu"])
    arpu_prev = safe_float(prev["arpu"])
    subs = safe_float(row["total_subscribers"])
    subs_prev = safe_float(prev["total_subscribers"])
    arpu_chg = percent_change(arpu, arpu_prev)
    subs_chg = percent_change(subs, subs_prev)
    if arpu_chg is None or subs_chg is None:
        return []
    if not (arpu_chg < 0 and subs_chg > 0):
        return []
    return [
        Recommendation(
            recommendation_id=f"REC-ARPU-SUBS-{month}",
            reporting_period=month,
            module="Revenue Analytics",
            finding=(
                f"ARPU fell {arpu_chg:.1f}% MoM while subscribers rose {subs_chg:.1f}%."
            ),
            metric_name="ARPU",
            metric_value=arpu,
            benchmark=arpu_prev,
            business_impact=(
                "Base expansion is diluting average revenue per user, "
                "pressuring contribution margin."
            ),
            recommended_action=(
                "Prioritise value-based offers and bundle upsell for new "
                "acquisitions; review entry-plan mix with Commercial."
            ),
            priority="High",
            responsible_department="Commercial",
            supporting_filters={"reporting_month": month},
        )
    ]


def rule_subscribers_up_revenue_down(
    executive_mart: pd.DataFrame,
    reporting_month: str,
) -> list[Recommendation]:
    """Flag subscriber growth concurrent with revenue decline."""
    row = row_for_month(executive_mart, reporting_month)
    month = str(row["reporting_month"])
    prev = _previous_row(executive_mart, month)
    if prev is None:
        return []
    rev = safe_float(row["total_revenue"])
    rev_prev = safe_float(prev["total_revenue"])
    subs = safe_float(row["total_subscribers"])
    subs_prev = safe_float(prev["total_subscribers"])
    rev_chg = percent_change(rev, rev_prev)
    subs_chg = percent_change(subs, subs_prev)
    if rev_chg is None or subs_chg is None:
        return []
    if not (subs_chg > 0 and rev_chg < 0):
        return []
    return [
        Recommendation(
            recommendation_id=f"REC-SUBS-REV-{month}",
            reporting_period=month,
            module="Executive Overview",
            finding=(
                f"Subscribers grew {subs_chg:.1f}% while total revenue fell "
                f"{abs(rev_chg):.1f}% MoM."
            ),
            metric_name="Total Revenue",
            metric_value=rev,
            benchmark=rev_prev,
            business_impact=(
                "Top-line contraction despite a larger base signals weak "
                "monetisation or mix shift."
            ),
            recommended_action=(
                "Investigate plan mix and recharge intensity; align Sales "
                "targets to revenue quality, not headcount alone."
            ),
            priority="Critical",
            responsible_department="Finance",
            supporting_filters={"reporting_month": month},
        )
    ]


def rule_high_value_churn_elevated(
    churn_mart: pd.DataFrame,
    reporting_month: str,
) -> list[Recommendation]:
    """Flag months where high-value churn exceeds the trailing average."""
    row = row_for_month(churn_mart, reporting_month)
    month = str(row["reporting_month"])
    current = safe_float(row["high_value_churned"])
    history = churn_mart[churn_mart["reporting_month"].astype(str) < month][
        "high_value_churned"
    ]
    if history.empty:
        return []
    benchmark = float(history.mean())
    if current <= 0 or current <= benchmark:
        return []
    return [
        Recommendation(
            recommendation_id=f"REC-HV-CHURN-{month}",
            reporting_period=month,
            module="Churn and Retention",
            finding=(
                f"High-value churned customers ({int(current)}) exceed the "
                f"historical average ({benchmark:.1f})."
            ),
            metric_name="High-Value Churned Customers",
            metric_value=current,
            benchmark=benchmark,
            business_impact=(
                "Loss of high-value subscribers disproportionately damages "
                "future ARPU and lifetime value."
            ),
            recommended_action=(
                "Trigger save offers and outbound retention for High/Very High "
                "Value at-risk cohorts via Customer Experience."
            ),
            priority="Critical",
            responsible_department="Customer Experience",
            supporting_filters={
                "reporting_month": month,
                "value_segment": "High Value,Very High Value",
            },
        )
    ]


def rule_data_growth_arpu_flat(
    revenue_mart: pd.DataFrame,
    reporting_month: str,
) -> list[Recommendation]:
    """Flag rising data usage while ARPU is flat or declining."""
    row = row_for_month(revenue_mart, reporting_month)
    month = str(row["reporting_month"])
    data = safe_float(row["data_mb"])
    data_prev = optional_float(row.get("data_mb_previous_month_value"))
    arpu = safe_float(row["arpu"])
    arpu_prev = optional_float(row.get("arpu_previous_month_value"))
    data_chg = percent_change(data, data_prev)
    arpu_chg = percent_change(arpu, arpu_prev)
    if data_chg is None or arpu_chg is None:
        return []
    if not (data_chg > 0 and arpu_chg <= ARPU_FLAT_BAND_PCT):
        return []
    return [
        Recommendation(
            recommendation_id=f"REC-DATA-ARPU-{month}",
            reporting_period=month,
            module="Revenue Analytics",
            finding=(
                f"Data usage rose {data_chg:.1f}% MoM while ARPU change was "
                f"{arpu_chg:.1f}% (flat/down band)."
            ),
            metric_name="Data Usage Volume",
            metric_value=data,
            benchmark=data_prev if data_prev is not None else 0.0,
            business_impact=(
                "Traffic growth without ARPU lift suggests under-monetised "
                "data consumption."
            ),
            recommended_action=(
                "Review data bundle ladders and fair-usage pricing with "
                "Commercial; test premium speed tiers."
            ),
            priority="Medium",
            responsible_department="Commercial",
            supporting_filters={"reporting_month": month},
        )
    ]


def rule_recharge_frequency_decline(
    recharge_mart: pd.DataFrame,
    reporting_month: str,
) -> list[Recommendation]:
    """Flag declining recharge frequency."""
    row = row_for_month(recharge_mart, reporting_month)
    month = str(row["reporting_month"])
    freq = safe_float(row["recharge_frequency"])
    prev = optional_float(row.get("recharge_frequency_previous_month_value"))
    chg = percent_change(freq, prev)
    if chg is None or chg >= 0:
        return []
    return [
        Recommendation(
            recommendation_id=f"REC-RECHARGE-FREQ-{month}",
            reporting_period=month,
            module="Recharge Analytics",
            finding=f"Recharge frequency declined {abs(chg):.1f}% MoM.",
            metric_name="Recharge Frequency",
            metric_value=freq,
            benchmark=prev if prev is not None else 0.0,
            business_impact=(
                "Fewer top-ups per active customer reduces near-term cash "
                "inflow and engagement."
            ),
            recommended_action=(
                "Deploy targeted top-up nudges and denomination experiments "
                "for valuable segments via Marketing."
            ),
            priority="High",
            responsible_department="Marketing",
            supporting_filters={"reporting_month": month},
        )
    ]


def rule_regional_subs_up_revenue_down(
    regional_mart: pd.DataFrame,
    reporting_month: str,
) -> list[Recommendation]:
    """Flag regions where subscribers grow but revenue falls."""
    month = pd.Timestamp(reporting_month).strftime("%Y-%m-%d")
    frame = regional_mart[regional_mart["reporting_month"].astype(str) == month]
    out: list[Recommendation] = []
    for _, row in frame.iterrows():
        subs = safe_float(row["subscribers"])
        subs_prev = optional_float(row.get("subscribers_previous_month_value"))
        rev = safe_float(row["total_revenue"])
        rev_prev = optional_float(row.get("total_revenue_previous_month_value"))
        subs_chg = percent_change(subs, subs_prev)
        rev_chg = percent_change(rev, rev_prev)
        if subs_chg is None or rev_chg is None:
            continue
        if not (subs_chg > 0 and rev_chg < 0):
            continue
        region = str(row["region"])
        out.append(
            Recommendation(
                recommendation_id=f"REC-REGION-{region.replace(' ', '')}-{month}",
                reporting_period=month,
                module="Regional Performance",
                finding=(
                    f"{region}: subscribers +{subs_chg:.1f}% MoM while "
                    f"revenue {rev_chg:.1f}%."
                ),
                metric_name="Regional Revenue",
                metric_value=rev,
                benchmark=rev_prev if rev_prev is not None else 0.0,
                business_impact=(
                    "Regional base growth is not translating into revenue, "
                    "indicating local mix or pricing issues."
                ),
                recommended_action=(
                    "Brief Regional Operations on monetisation plays and "
                    "audit local offer compliance."
                ),
                priority="High",
                responsible_department="Regional Operations",
                supporting_filters={"reporting_month": month, "region": region},
            )
        )
    return out


def rule_negative_campaign_roi(
    campaign_mart: pd.DataFrame,
    reporting_period: str,
) -> list[Recommendation]:
    """Flag campaigns with negative ROI."""
    out: list[Recommendation] = []
    for _, row in campaign_mart.iterrows():
        roi = safe_float(row["roi"])
        if roi >= 0:
            continue
        campaign_id = str(row["campaign_id"])
        out.append(
            Recommendation(
                recommendation_id=f"REC-CAMPAIGN-ROI-{campaign_id}",
                reporting_period=reporting_period,
                module="Campaign Analytics",
                finding=(
                    f"Campaign {campaign_id} has negative ROI ({roi * 100.0:.1f}%)."
                ),
                metric_name="Campaign ROI",
                metric_value=roi * 100.0,
                benchmark=0.0,
                business_impact=(
                    "Marketing spend is not recovering incremental attributed "
                    "revenue for this campaign."
                ),
                recommended_action=(
                    "Pause or redesign targeting and creative; reallocate "
                    "budget to positive-ROI campaigns."
                ),
                priority="High",
                responsible_department="Marketing",
                supporting_filters={"campaign_id": campaign_id},
            )
        )
    return out


def rule_high_conversion_weak_retention(
    campaign_mart: pd.DataFrame,
    reporting_period: str,
) -> list[Recommendation]:
    """Flag high conversion with weak 30-day retention among converters."""
    out: list[Recommendation] = []
    for _, row in campaign_mart.iterrows():
        conversion_rate = safe_float(row["conversion_rate"])
        conversions = safe_float(row["conversions"])
        retained = safe_float(row["retained_after_30_days"])
        if conversions <= 0:
            continue
        retention_ratio = retained / conversions
        if not (
            conversion_rate >= HIGH_CONVERSION_RATE
            and retention_ratio < WEAK_RETENTION_RATIO
        ):
            continue
        campaign_id = str(row["campaign_id"])
        out.append(
            Recommendation(
                recommendation_id=f"REC-CAMPAIGN-RET-{campaign_id}",
                reporting_period=reporting_period,
                module="Campaign Analytics",
                finding=(
                    f"Campaign {campaign_id} converts well "
                    f"({conversion_rate * 100.0:.1f}%) but only "
                    f"{retention_ratio * 100.0:.1f}% of converters remain "
                    "after 30 days."
                ),
                metric_name="Post-Campaign Retention Ratio",
                metric_value=retention_ratio * 100.0,
                benchmark=WEAK_RETENTION_RATIO * 100.0,
                business_impact=(
                    "Acquisition wins are leaking quickly, lowering campaign "
                    "payback and inflating churn."
                ),
                recommended_action=(
                    "Add onboarding and day-7/day-30 nurture journeys for "
                    "converters; tighten offer eligibility."
                ),
                priority="Medium",
                responsible_department="Marketing",
                supporting_filters={"campaign_id": campaign_id},
            )
        )
    return out


def rule_dormant_streak(
    subscriber_mart: pd.DataFrame,
    reporting_month: str,
) -> list[Recommendation]:
    """Flag consecutive monthly increases in dormant subscribers."""
    month = pd.Timestamp(reporting_month).strftime("%Y-%m-%d")
    ordered = subscriber_mart.sort_values("reporting_month").reset_index(drop=True)
    idx_list = ordered.index[ordered["reporting_month"].astype(str) == month].tolist()
    if not idx_list:
        return []
    idx = int(idx_list[0])
    if idx < DORMANT_STREAK_MONTHS:
        return []
    window = ordered.iloc[idx - DORMANT_STREAK_MONTHS : idx + 1]
    dormant = window["dormant_subscribers"].astype(float).tolist()
    increases = all(dormant[i] > dormant[i - 1] for i in range(1, len(dormant)))
    if not increases:
        return []
    current = dormant[-1]
    baseline = dormant[0]
    return [
        Recommendation(
            recommendation_id=f"REC-DORMANT-{month}",
            reporting_period=month,
            module="Subscriber Analytics",
            finding=(
                f"Dormant subscribers rose for {DORMANT_STREAK_MONTHS} "
                f"consecutive months (from {baseline:.0f} to {current:.0f})."
            ),
            metric_name="Dormant Subscribers",
            metric_value=current,
            benchmark=baseline,
            business_impact=(
                "A lengthening dormant pool raises future churn risk and "
                "reduces recoverable revenue."
            ),
            recommended_action=(
                "Launch win-back and low-denomination reactivation campaigns "
                "focused on dormant cohorts."
            ),
            priority="High",
            responsible_department="Customer Experience",
            supporting_filters={
                "reporting_month": month,
                "lifecycle_status": "Dormant",
            },
        )
    ]


def rule_churn_above_rolling_average(
    churn_mart: pd.DataFrame,
    reporting_month: str,
) -> list[Recommendation]:
    """Flag churn rate above its rolling 3-month average."""
    row = row_for_month(churn_mart, reporting_month)
    month = str(row["reporting_month"])
    churn = safe_float(row["churn_rate"])
    rolling = optional_float(row.get("churn_rate_rolling_3_month_average"))
    if rolling is None or churn <= rolling:
        return []
    return [
        Recommendation(
            recommendation_id=f"REC-CHURN-ROLL-{month}",
            reporting_period=month,
            module="Churn and Retention",
            finding=(
                f"Churn rate {churn:.3f}% is above the rolling 3-month "
                f"average of {rolling:.3f}%."
            ),
            metric_name="Churn Rate",
            metric_value=churn,
            benchmark=rolling,
            business_impact=(
                "Elevated churn versus the recent trend increases revenue "
                "at risk this quarter."
            ),
            recommended_action=(
                "Escalate retention playbooks for At Risk customers and "
                "review tenure hotspots with Customer Experience."
            ),
            priority="High",
            responsible_department="Customer Experience",
            supporting_filters={"reporting_month": month},
        )
    ]


def _previous_row(frame: pd.DataFrame, reporting_month: str) -> pd.Series | None:
    month_ts = pd.Timestamp(reporting_month)
    prev_month = (month_ts - pd.offsets.MonthBegin(1)).strftime("%Y-%m-%d")
    matched = frame[frame["reporting_month"].astype(str) == prev_month]
    if matched.empty:
        return None
    return matched.iloc[0]
