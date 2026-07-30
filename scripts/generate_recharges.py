"""CLI: generate recharge dataset.

Example:
    python -m scripts.generate_recharges --profile development
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from src.config import list_profiles, load_settings
from src.generator.io import read_frame
from src.generator.transactions import generate_recharge_dataset
from src.utils.logging import configure_logging, get_logger
from src.validation.transactions import validate_recharges

logger = get_logger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    """Generate and validate recharges for a profile."""
    parser = argparse.ArgumentParser(description="Generate synthetic recharge data.")
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
        path = generate_recharge_dataset(settings)

        recharges = read_frame(path)
        customers = read_frame(settings.raw_data_path / "customers.parquet")
        products = read_frame(settings.reference_data_path / "products.csv")
        report = validate_recharges(recharges, customers, products)
        for warning in report.warnings:
            logger.warning("[%s] %s", report.dataset, warning)
        for error in report.errors:
            logger.error("[%s] %s", report.dataset, error)
        if not report.ok:
            return 1

        logger.info(
            "Recharge generation succeeded (%s rows). Mean amount=%.2f TZS",
            f"{len(recharges):,}",
            float(recharges["amount"].mean()),
        )
        return 0
    except Exception:
        logger.exception("Recharge generation failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
