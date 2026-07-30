"""CLI: generate customer events and monthly lifecycle snapshots.

Example:
    python -m scripts.generate_customer_events --profile development
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from src.config import list_profiles, load_settings
from src.generator.io import read_frame
from src.generator.lifecycle_pipeline import generate_lifecycle_datasets
from src.utils.logging import configure_logging, get_logger
from src.validation.lifecycle import validate_customer_events, validate_snapshot

logger = get_logger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    """Generate and validate lifecycle snapshot and customer events."""
    parser = argparse.ArgumentParser(
        description="Generate customer events and monthly lifecycle snapshots."
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
        paths = generate_lifecycle_datasets(settings)

        customers = read_frame(settings.raw_data_path / "customers.parquet")
        snapshot = read_frame(paths["customer_monthly_snapshot"])
        events = read_frame(paths["customer_events"])

        reports = [
            validate_snapshot(snapshot, customers),
            validate_customer_events(events, customers),
        ]
        for report in reports:
            for warning in report.warnings:
                logger.warning("[%s] %s", report.dataset, warning)
            for error in report.errors:
                logger.error("[%s] %s", report.dataset, error)
            if not report.ok:
                return 1

        churned = int(snapshot["newly_churned"].sum())
        reactivated = int(snapshot["newly_reactivated"].sum())
        logger.info(
            "Lifecycle generation succeeded. Snapshot=%s rows, events=%s, "
            "newly_churned=%s, newly_reactivated=%s",
            f"{len(snapshot):,}",
            f"{len(events):,}",
            churned,
            reactivated,
        )
        return 0
    except Exception:
        logger.exception("Lifecycle generation failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
