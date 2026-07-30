"""Analytics service package (business calculations live here)."""

from src.analytics.breakdowns import (
    filter_month_range,
    regional_revenue_slice,
    revenue_by_value_segment,
)
from src.analytics.campaign_regional import campaign_kpi_summary, regional_kpi_cards
from src.analytics.comparisons import (
    absolute_change,
    percent_change,
    percentage_point_change,
    period_snapshot,
)
from src.analytics.domain import (
    mobile_money_kpi_cards,
    recharge_kpi_cards,
    retention_kpi_cards,
    subscriber_kpi_cards,
)
from src.analytics.executive import executive_kpi_cards, revenue_kpi_cards
from src.analytics.loaders import load_mart, row_for_month
from src.analytics.types import KpiResult

__all__ = [
    "KpiResult",
    "absolute_change",
    "campaign_kpi_summary",
    "executive_kpi_cards",
    "filter_month_range",
    "load_mart",
    "mobile_money_kpi_cards",
    "percent_change",
    "percentage_point_change",
    "period_snapshot",
    "recharge_kpi_cards",
    "regional_kpi_cards",
    "regional_revenue_slice",
    "retention_kpi_cards",
    "revenue_by_value_segment",
    "revenue_kpi_cards",
    "row_for_month",
    "subscriber_kpi_cards",
]
