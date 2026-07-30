"""Build processed fact tables from raw transactional datasets."""

from __future__ import annotations

import pandas as pd

from src.utils.logging import get_logger

logger = get_logger(__name__)


def build_fact_usage_daily(usage: pd.DataFrame) -> pd.DataFrame:
    """Build daily usage fact with date_key."""
    fact = usage.copy()
    fact["date_key"] = (
        pd.to_datetime(fact["usage_date"]).dt.strftime("%Y%m%d").astype(int)
    )
    fact["usage_date"] = pd.to_datetime(fact["usage_date"]).dt.strftime("%Y-%m-%d")
    logger.info("Built fact_usage_daily (%s rows)", f"{len(fact):,}")
    return fact


def build_fact_recharge(recharges: pd.DataFrame) -> pd.DataFrame:
    """Build recharge fact."""
    fact = recharges.copy()
    ts = pd.to_datetime(fact["recharge_timestamp"])
    fact["date_key"] = ts.dt.strftime("%Y%m%d").astype(int)
    fact["recharge_date"] = ts.dt.strftime("%Y-%m-%d")
    if fact["recharge_id"].duplicated().any():
        raise ValueError("fact_recharge has duplicate recharge_id values.")
    logger.info("Built fact_recharge (%s rows)", f"{len(fact):,}")
    return fact


def build_fact_mobile_money(mobile_money: pd.DataFrame) -> pd.DataFrame:
    """Build mobile money fact."""
    fact = mobile_money.copy()
    ts = pd.to_datetime(fact["transaction_timestamp"])
    fact["date_key"] = ts.dt.strftime("%Y%m%d").astype(int)
    fact["transaction_date"] = ts.dt.strftime("%Y-%m-%d")
    if fact["transaction_id"].duplicated().any():
        raise ValueError("fact_mobile_money has duplicate transaction_id values.")
    logger.info("Built fact_mobile_money (%s rows)", f"{len(fact):,}")
    return fact


def build_fact_campaign_response(responses: pd.DataFrame) -> pd.DataFrame:
    """Build campaign response fact."""
    fact = responses.copy()
    logger.info("Built fact_campaign_response (%s rows)", f"{len(fact):,}")
    return fact


def build_fact_customer_events(events: pd.DataFrame) -> pd.DataFrame:
    """Build customer events fact."""
    fact = events.copy()
    ts = pd.to_datetime(fact["event_timestamp"])
    fact["date_key"] = ts.dt.strftime("%Y%m%d").astype(int)
    if fact["event_id"].duplicated().any():
        raise ValueError("fact_customer_events has duplicate event_id values.")
    logger.info("Built fact_customer_events (%s rows)", f"{len(fact):,}")
    return fact
