"""Campaign response generation with targeting-relevance effects."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from src.config.settings import AppSettings
from src.utils.logging import get_logger

logger = get_logger(__name__)


def _relevance(
    customer_segment: str,
    customer_region: str,
    target_segment: str,
    target_region: str | None,
) -> str:
    """Classify targeting relevance for a customer-campaign pair."""
    segment_match = customer_segment == target_segment
    region_match = target_region is None or customer_region == target_region
    if segment_match and region_match:
        return "relevant"
    if segment_match or region_match:
        return "partial"
    return "irrelevant"


def _probs(relevance: str) -> tuple[float, float, float]:
    """Return (contact, response|contact, conversion|response) probabilities."""
    if relevance == "relevant":
        return 0.55, 0.42, 0.38
    if relevance == "partial":
        return 0.25, 0.22, 0.18
    return 0.12, 0.10, 0.08


def generate_campaign_responses(
    settings: AppSettings,
    customers: pd.DataFrame,
    campaigns: pd.DataFrame,
    *,
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    """Generate campaign-response outcomes for all campaigns.

    Contact/response/conversion probabilities are higher when the customer
    matches the campaign target segment (and region when specified).

    Args:
        settings: Application settings (seed).
        customers: Customer master.
        campaigns: Campaign catalogue.
        rng: Optional numpy Generator.

    Returns:
        Campaign responses DataFrame (one row per contacted or sampled pair).
    """
    base_rng = rng or np.random.default_rng(settings.random_seed + 404)
    rows: list[dict[str, object]] = []

    cust = customers[
        ["customer_id", "customer_segment", "region", "registration_date"]
    ].copy()
    cust["registration_date"] = pd.to_datetime(cust["registration_date"]).dt.date

    for campaign in campaigns.itertuples(index=False):
        start = date.fromisoformat(str(campaign.start_date))
        end = date.fromisoformat(str(campaign.end_date))
        target_segment = str(campaign.target_segment)
        target_region = (
            None
            if campaign.target_region is None or str(campaign.target_region) == "nan"
            else str(campaign.target_region)
        )

        eligible = cust[cust["registration_date"] <= end]
        logger.info(
            "Generating responses for %s (%s eligible customers)",
            campaign.campaign_id,
            f"{len(eligible):,}",
        )

        # Oversample target segment for contact consideration.
        segment_mask = eligible["customer_segment"] == target_segment
        if target_region is not None:
            region_mask = eligible["region"] == target_region
        else:
            region_mask = pd.Series(True, index=eligible.index)

        priority = eligible[segment_mask | region_mask]
        other = eligible[~(segment_mask | region_mask)]

        # Cap evaluation set for development scale while keeping representativeness.
        n_priority = min(len(priority), max(800, int(0.35 * len(eligible))))
        n_other = min(len(other), max(400, int(0.15 * len(eligible))))
        sample_parts: list[pd.DataFrame] = []
        if n_priority > 0:
            sample_parts.append(
                priority.sample(
                    n=n_priority, random_state=int(base_rng.integers(0, 1_000_000_000))
                )
            )
        if n_other > 0:
            sample_parts.append(
                other.sample(
                    n=n_other, random_state=int(base_rng.integers(0, 1_000_000_000))
                )
            )
        if not sample_parts:
            continue
        sample = pd.concat(sample_parts, ignore_index=True)

        for customer in sample.itertuples(index=False):
            relevance = _relevance(
                str(customer.customer_segment),
                str(customer.region),
                target_segment,
                target_region,
            )
            p_contact, p_response, p_convert = _probs(relevance)
            contacted = bool(base_rng.random() < p_contact)
            if not contacted:
                continue

            responded = bool(base_rng.random() < p_response)
            converted = bool(responded and base_rng.random() < p_convert)

            conversion_date = None
            revenue_generated = 0.0
            if converted:
                offset = int(base_rng.integers(0, (end - start).days + 1))
                conversion_date = (start + timedelta(days=offset)).isoformat()
                # Observed attributable revenue proxy (not causal uplift).
                base_rev = {
                    "relevant": 18_000.0,
                    "partial": 9_000.0,
                    "irrelevant": 4_000.0,
                }[relevance]
                revenue_generated = float(
                    np.round(base_rev * base_rng.lognormal(0.0, 0.35), 2)
                )

            pre = float(np.round(base_rng.lognormal(8.5, 0.5), 2))
            during = float(
                np.round(
                    pre * (1.25 if converted else 1.02) * base_rng.uniform(0.9, 1.1), 2
                )
            )
            post = float(
                np.round(
                    during
                    * (1.05 if converted else 0.95)
                    * base_rng.uniform(0.85, 1.1),
                    2,
                )
            )

            retained = bool(
                converted
                and base_rng.random() < (0.72 if relevance == "relevant" else 0.55)
            )
            churned = bool(
                contacted
                and not retained
                and base_rng.random() < (0.04 if relevance == "relevant" else 0.08)
            )

            rows.append(
                {
                    "campaign_id": campaign.campaign_id,
                    "customer_id": customer.customer_id,
                    "targeting_relevance": relevance,
                    "contacted": contacted,
                    "responded": responded,
                    "converted": converted,
                    "conversion_date": conversion_date,
                    "revenue_generated": revenue_generated,
                    "pre_campaign_revenue": pre,
                    "campaign_period_revenue": during,
                    "post_campaign_revenue": post,
                    "retained_after_30_days": retained,
                    "churned_after_campaign": churned,
                }
            )

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)
