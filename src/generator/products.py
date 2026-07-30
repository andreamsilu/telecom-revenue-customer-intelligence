"""Synthetic telecom product catalogue generation."""

from __future__ import annotations

from datetime import date

import pandas as pd

from src.config.settings import AppSettings


def generate_products(settings: AppSettings) -> pd.DataFrame:
    """Build the Version 1 product and service catalogue in TZS.

    Args:
        settings: Application settings (used for active date window).

    Returns:
        Product reference DataFrame.
    """
    active_from = settings.start_date.isoformat()
    catalog: list[dict[str, object]] = [
        {
            "product_id": "PRD-VOICE-PER-MIN",
            "product_name": "Domestic Voice Per Minute",
            "product_category": "voice",
            "service_type": "usage",
            "unit_price": 35.0,
            "bundle_size": None,
            "validity_days": None,
            "target_segment": "Mass Market",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-SMS-EACH",
            "product_name": "Domestic SMS",
            "product_category": "SMS",
            "service_type": "usage",
            "unit_price": 15.0,
            "bundle_size": None,
            "validity_days": None,
            "target_segment": "Mass Market",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-DATA-PAYG-MB",
            "product_name": "Pay-As-You-Go Data MB",
            "product_category": "data",
            "service_type": "usage",
            "unit_price": 12.0,
            "bundle_size": 1.0,
            "validity_days": None,
            "target_segment": "Digital First",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-DATA-500MB-7D",
            "product_name": "Student 500MB / 7 Days",
            "product_category": "data_bundle",
            "service_type": "bundle",
            "unit_price": 1500.0,
            "bundle_size": 500.0,
            "validity_days": 7,
            "target_segment": "Youth",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-DATA-1GB-7D",
            "product_name": "Data 1GB / 7 Days",
            "product_category": "data_bundle",
            "service_type": "bundle",
            "unit_price": 2500.0,
            "bundle_size": 1024.0,
            "validity_days": 7,
            "target_segment": "Mass Market",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-DATA-5GB-30D",
            "product_name": "Data 5GB / 30 Days",
            "product_category": "data_bundle",
            "service_type": "bundle",
            "unit_price": 10000.0,
            "bundle_size": 5120.0,
            "validity_days": 30,
            "target_segment": "Digital First",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-DATA-15GB-30D",
            "product_name": "Data 15GB / 30 Days",
            "product_category": "data_bundle",
            "service_type": "bundle",
            "unit_price": 25000.0,
            "bundle_size": 15360.0,
            "validity_days": 30,
            "target_segment": "High Value",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-VOICE-100-7D",
            "product_name": "Voice 100 Minutes / 7 Days",
            "product_category": "voice_bundle",
            "service_type": "bundle",
            "unit_price": 2000.0,
            "bundle_size": 100.0,
            "validity_days": 7,
            "target_segment": "Rural",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-SMS-100-7D",
            "product_name": "SMS 100 / 7 Days",
            "product_category": "SMS_bundle",
            "service_type": "bundle",
            "unit_price": 1000.0,
            "bundle_size": 100.0,
            "validity_days": 7,
            "target_segment": "Mass Market",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-COMBO-DAILY",
            "product_name": "Daily Combo Voice+Data",
            "product_category": "combo_bundle",
            "service_type": "bundle",
            "unit_price": 1000.0,
            "bundle_size": None,
            "validity_days": 1,
            "target_segment": "Youth",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-COMBO-SME-30D",
            "product_name": "SME Combo 30 Days",
            "product_category": "combo_bundle",
            "service_type": "bundle",
            "unit_price": 35000.0,
            "bundle_size": None,
            "validity_days": 30,
            "target_segment": "SME",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-INTL-PER-MIN",
            "product_name": "International Voice Per Minute",
            "product_category": "international",
            "service_type": "usage",
            "unit_price": 450.0,
            "bundle_size": None,
            "validity_days": None,
            "target_segment": "High Value",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-ROAM-PER-MIN",
            "product_name": "Roaming Voice Per Minute",
            "product_category": "roaming",
            "service_type": "usage",
            "unit_price": 800.0,
            "bundle_size": None,
            "validity_days": None,
            "target_segment": "Corporate",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-VAS-RING",
            "product_name": "Caller Tune VAS",
            "product_category": "VAS",
            "service_type": "subscription",
            "unit_price": 500.0,
            "bundle_size": None,
            "validity_days": 30,
            "target_segment": "Youth",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-MM-WALLET",
            "product_name": "Mobile Money Wallet",
            "product_category": "mobile_money",
            "service_type": "wallet",
            "unit_price": 0.0,
            "bundle_size": None,
            "validity_days": None,
            "target_segment": "SME",
            "active_from": active_from,
            "active_to": None,
        },
        {
            "product_id": "PRD-CORP-PLAN",
            "product_name": "Corporate Voice+Data Plan",
            "product_category": "combo_bundle",
            "service_type": "plan",
            "unit_price": 120000.0,
            "bundle_size": None,
            "validity_days": 30,
            "target_segment": "Corporate",
            "active_from": active_from,
            "active_to": None,
        },
    ]

    frame = pd.DataFrame(catalog)
    if frame["product_id"].duplicated().any():
        raise ValueError("Duplicate product_id values in catalogue.")
    if (frame["unit_price"] < 0).any():
        raise ValueError("Product unit_price must be non-negative.")
    # Guard: active_from must not be after project end.
    _ = date.fromisoformat(active_from)
    return frame
