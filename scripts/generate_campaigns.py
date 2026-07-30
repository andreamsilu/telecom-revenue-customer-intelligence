"""CLI: generate campaigns and campaign responses.

Example:
    python -m scripts.generate_campaigns --profile development
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from src.config import list_profiles, load_settings
from src.generator.engagement import generate_campaign_datasets
from src.generator.io import read_frame
from src.utils.logging import configure_logging, get_logger
from src.validation.engagement import (
    validate_campaign_responses,
    validate_campaigns,
)

logger = get_logger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    """Generate and validate campaigns and responses for a profile."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic campaigns and campaign responses."
    )
    parser.add_argument(
        "--profile",
        choices=list_profiles(),
        default="development",
        help="Configuration profile (default: development).",
    )
    args = parser.parse_args(argv)

    try:
        settings = load_settings(profile_name=args.profile)
        configure_logging(settings.logging_level, force=True)
        paths = generate_campaign_datasets(settings)

        campaigns = read_frame(paths["campaigns"])
        responses = read_frame(paths["campaign_responses"])
        customers = read_frame(settings.raw_data_path / "customers.parquet")
        products = read_frame(settings.reference_data_path / "products.csv")

        reports = [
            validate_campaigns(campaigns, products),
            validate_campaign_responses(responses, customers, campaigns),
        ]
        for report in reports:
            for warning in report.warnings:
                logger.warning("[%s] %s", report.dataset, warning)
            for error in report.errors:
                logger.error("[%s] %s", report.dataset, error)
            if not report.ok:
                return 1

        if "targeting_relevance" in responses.columns:
            rates = (
                responses.groupby("targeting_relevance")["converted"].mean().to_dict()
            )
            logger.info("Conversion rate by relevance: %s", rates)

        logger.info(
            "Campaign generation succeeded (%s campaigns, %s responses).",
            len(campaigns),
            f"{len(responses):,}",
        )
        return 0
    except Exception:
        logger.exception("Campaign generation failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
