"""CLI health check for configuration, paths, and package imports.

Example:
    python -m scripts.health_check --profile development
"""

from __future__ import annotations

import argparse
import importlib
import sys
from collections.abc import Sequence

from src.config import ProfileName, list_profiles, load_settings
from src.utils.logging import configure_logging, get_logger
from src.utils.paths import ensure_data_directories, get_repo_root, relative_to_repo

logger = get_logger(__name__)

_REQUIRED_PACKAGES: tuple[str, ...] = (
    "pandas",
    "numpy",
    "pyarrow",
    "pydantic",
    "pydantic_settings",
    "dotenv",
    "faker",
)


def run_health_check(
    profile: ProfileName = "development",
    *,
    create_directories: bool | None = None,
) -> int:
    """Validate configuration, paths, and critical package imports.

    Args:
        profile: Named scale profile to load.
        create_directories: Override whether missing data dirs are created.

    Returns:
        Process exit code: 0 on success, 1 on failure.
    """
    try:
        settings = load_settings(profile_name=profile)
        if create_directories is not None:
            settings = settings.model_copy(
                update={"create_directories": create_directories}
            )

        configure_logging(settings.logging_level, force=True)
        log = get_logger(__name__)

        repo_root = get_repo_root()
        log.info("Repository root: %s", repo_root)
        log.info("Project: %s", settings.project_name)
        log.info("Profile: %s", settings.profile_name)
        log.info(
            "Period: %s → %s (%d months)",
            settings.start_date,
            settings.end_date,
            len(settings.period_month_starts()),
        )
        log.info("Reporting month: %s", settings.reporting_month.isoformat())
        log.info("Subscriber count: %s", f"{settings.subscriber_count:,}")
        log.info("Random seed: %s", settings.random_seed)
        log.info("Batch size: %s", f"{settings.batch_size:,}")

        directories = settings.required_data_directories()
        for directory in directories:
            rel = relative_to_repo(directory, repo_root)
            exists = directory.exists()
            log.info(
                "Data path %-12s → %s (%s)",
                directory.name,
                rel,
                "exists" if exists else "missing",
            )

        if settings.create_directories:
            ensure_data_directories(directories)
            log.info("Ensured required data directories exist.")

        missing = [p for p in directories if not p.exists()]
        if missing:
            names = ", ".join(str(relative_to_repo(p, repo_root)) for p in missing)
            raise FileNotFoundError(f"Required directories missing: {names}")

        for package_name in _REQUIRED_PACKAGES:
            importlib.import_module(package_name)
            log.info("Import OK: %s", package_name)

        # Confirm internal packages import cleanly.
        importlib.import_module("src.config")
        importlib.import_module("src.utils")
        log.info("Internal packages import OK.")
        log.info("Health check passed for profile '%s'.", profile)
        return 0
    except Exception:
        logger.exception("Health check failed for profile '%s'.", profile)
        return 1


def build_parser() -> argparse.ArgumentParser:
    """Build the health-check argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Validate configuration, resolve data paths, and confirm "
            "package imports for the Telecom Revenue & Customer "
            "Intelligence Platform."
        )
    )
    parser.add_argument(
        "--profile",
        choices=list_profiles(),
        default="development",
        help="Configuration profile to load (default: development).",
    )
    parser.add_argument(
        "--no-create-directories",
        action="store_true",
        help="Do not create missing data directories.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse CLI arguments and run the health check."""
    parser = build_parser()
    args = parser.parse_args(argv)
    create_directories = False if args.no_create_directories else None
    return run_health_check(
        profile=args.profile,
        create_directories=create_directories,
    )


if __name__ == "__main__":
    sys.exit(main())
