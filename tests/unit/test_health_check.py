"""Unit tests for the CLI health check."""

from __future__ import annotations

from scripts.health_check import main, run_health_check


def test_health_check_succeeds_for_development_profile() -> None:
    """Development profile health check returns exit code 0."""
    exit_code = run_health_check(profile="development", create_directories=True)
    assert exit_code == 0


def test_health_check_main_cli() -> None:
    """CLI entry point accepts --profile development."""
    exit_code = main(["--profile", "development"])
    assert exit_code == 0
