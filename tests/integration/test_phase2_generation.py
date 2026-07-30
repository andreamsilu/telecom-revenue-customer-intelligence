"""Integration tests for Phase 2 generation CLIs and persistence."""

from __future__ import annotations

from pathlib import Path

from scripts.generate_customers import main as generate_customers_main
from scripts.generate_reference_data import main as generate_reference_main
from src.config import load_settings
from src.generator.io import read_frame
from src.validation import validate_customers


def test_reference_and_customer_cli_development(
    tmp_path: Path,
    monkeypatch: object,
) -> None:
    """CLI generation writes valid reference and customer datasets."""
    settings = load_settings(
        profile_name="development",
        subscriber_count=250,
        reference_data_path=tmp_path / "reference",
        raw_data_path=tmp_path / "raw",
    )

    # Patch load_settings used inside CLI modules.
    def _load(profile_name: str = "development", **overrides: object):  # type: ignore[no-untyped-def]
        return load_settings(
            profile_name=profile_name,
            subscriber_count=250,
            reference_data_path=tmp_path / "reference",
            raw_data_path=tmp_path / "raw",
            **overrides,
        )

    import scripts.generate_customers as cust_cli
    import scripts.generate_reference_data as ref_cli

    monkeypatch.setattr(ref_cli, "load_settings", _load)
    monkeypatch.setattr(cust_cli, "load_settings", _load)

    assert generate_reference_main(["--profile", "development"]) == 0
    assert (tmp_path / "reference" / "calendar.csv").exists()
    assert (tmp_path / "reference" / "regions.csv").exists()
    assert (tmp_path / "reference" / "products.csv").exists()

    assert generate_customers_main(["--profile", "development"]) == 0
    customers_path = tmp_path / "raw" / "customers.parquet"
    assert customers_path.exists()

    customers = read_frame(customers_path)
    regions = read_frame(tmp_path / "reference" / "regions.csv")
    report = validate_customers(customers, regions, expected_count=250)
    assert report.ok, report.errors
    assert settings.subscriber_count == 250
