"""Synthetic data generation package."""

from __future__ import annotations

from src.generator.calendar import generate_calendar
from src.generator.campaign_responses import generate_campaign_responses
from src.generator.campaigns import generate_campaigns
from src.generator.customers import generate_customers
from src.generator.engagement import (
    generate_campaign_datasets,
    generate_mobile_money_dataset,
)
from src.generator.mobile_money import generate_mobile_money
from src.generator.products import generate_products
from src.generator.recharges import generate_recharges
from src.generator.reference import (
    generate_customer_dataset,
    generate_reference_datasets,
)
from src.generator.regions import generate_regions
from src.generator.transactions import (
    generate_recharge_dataset,
    generate_usage_dataset,
)
from src.generator.usage import generate_daily_usage

__all__ = [
    "generate_calendar",
    "generate_campaign_datasets",
    "generate_campaign_responses",
    "generate_campaigns",
    "generate_customer_dataset",
    "generate_customers",
    "generate_daily_usage",
    "generate_mobile_money",
    "generate_mobile_money_dataset",
    "generate_products",
    "generate_recharge_dataset",
    "generate_recharges",
    "generate_reference_datasets",
    "generate_regions",
    "generate_usage_dataset",
]
