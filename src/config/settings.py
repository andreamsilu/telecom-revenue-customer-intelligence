"""Pydantic settings for project-wide configuration."""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.utils.paths import get_repo_root

ProfileName = Literal["development", "demo", "portfolio"]


def _add_months(value: date, months: int) -> date:
    """Return ``value`` advanced by ``months`` calendar months."""
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


class OutputFormat(StrEnum):
    """Supported on-disk formats for generated datasets."""

    PARQUET = "parquet"
    CSV = "csv"


class ValidationStrictness(StrEnum):
    """How validation failures are treated during pipelines."""

    STRICT = "strict"
    LENIENT = "lenient"


class AppSettings(BaseSettings):
    """Validated application settings for generation and analytics.

    Paths are resolved relative to the repository root unless absolute.
    """

    model_config = SettingsConfigDict(
        env_prefix="TRCI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_name: str = Field(
        default="Telecom Revenue & Customer Intelligence Platform",
        description="Human-readable project name.",
    )
    profile_name: ProfileName = Field(
        default="development",
        description="Active scale profile.",
    )
    random_seed: int = Field(
        default=42,
        ge=0,
        description="Deterministic random seed for synthetic generation.",
    )
    start_date: date = Field(
        default=date(2024, 1, 1),
        description="Inclusive start of the historical period.",
    )
    end_date: date = Field(
        default=date(2025, 12, 31),
        description="Inclusive end of the historical period.",
    )
    reporting_month: date = Field(
        default=date(2025, 12, 1),
        description="Default reporting month (normalized to month start).",
    )
    subscriber_count: int = Field(
        default=10_000,
        gt=0,
        description="Number of synthetic subscribers to generate.",
    )
    batch_size: int = Field(
        default=2_000,
        gt=0,
        description="Batch size for memory-conscious generation.",
    )
    raw_data_path: Path = Field(
        default=Path("data/raw"),
        description="Directory for raw generated datasets.",
    )
    processed_data_path: Path = Field(
        default=Path("data/processed"),
        description="Directory for processed analytical datasets.",
    )
    reference_data_path: Path = Field(
        default=Path("data/reference"),
        description="Directory for small reference datasets.",
    )
    export_path: Path = Field(
        default=Path("data/exports"),
        description="Directory for exported reports and extracts.",
    )
    raw_output_format: OutputFormat = Field(
        default=OutputFormat.PARQUET,
        description="On-disk format for large raw datasets.",
    )
    processed_output_format: OutputFormat = Field(
        default=OutputFormat.PARQUET,
        description="On-disk format for processed datasets and marts.",
    )
    validation_strictness: ValidationStrictness = Field(
        default=ValidationStrictness.STRICT,
        description="Whether validation failures abort pipelines.",
    )
    logging_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Root logging level for application modules.",
    )
    create_directories: bool = Field(
        default=True,
        description="Create missing data directories when resolving paths.",
    )

    @field_validator("reporting_month", mode="before")
    @classmethod
    def normalize_reporting_month(cls, value: date | str) -> date:
        """Normalize reporting month to the first day of the month."""
        if isinstance(value, str):
            value = date.fromisoformat(value)
        return value.replace(day=1)

    @field_validator(
        "raw_data_path",
        "processed_data_path",
        "reference_data_path",
        "export_path",
        mode="before",
    )
    @classmethod
    def coerce_path(cls, value: Path | str) -> Path:
        """Coerce string path values to Path objects."""
        return Path(value)

    @model_validator(mode="after")
    def validate_business_rules(self) -> Self:
        """Enforce date range, reporting month, and period length rules."""
        if self.subscriber_count <= 0:
            raise ValueError("subscriber_count must be a positive integer.")

        if self.start_date >= self.end_date:
            raise ValueError(
                f"start_date ({self.start_date}) must be earlier than "
                f"end_date ({self.end_date})."
            )

        period_start = self.start_date.replace(day=1)
        # End of the last complete month that includes end_date
        last_month_start = self.end_date.replace(day=1)
        month_count = (
            (last_month_start.year - period_start.year) * 12
            + (last_month_start.month - period_start.month)
            + 1
        )
        if month_count != 24:
            raise ValueError(
                f"Configured period must contain exactly 24 complete months; "
                f"found {month_count} months between {self.start_date} "
                f"and {self.end_date}."
            )

        reporting = self.reporting_month
        if reporting < period_start or reporting > last_month_start:
            raise ValueError(
                f"reporting_month ({reporting}) must fall within the data "
                f"range [{period_start}, {last_month_start}]."
            )

        if self.batch_size <= 0:
            raise ValueError("batch_size must be a positive integer.")

        return self

    def resolve_paths(self, repo_root: Path | None = None) -> AppSettings:
        """Return a copy with data paths resolved against the repository root.

        Args:
            repo_root: Optional explicit repository root. Defaults to detection.

        Returns:
            A new AppSettings instance with absolute data paths.
        """
        root = repo_root or get_repo_root()
        updates: dict[str, Path] = {}
        for field_name in (
            "raw_data_path",
            "processed_data_path",
            "reference_data_path",
            "export_path",
        ):
            path = getattr(self, field_name)
            updates[field_name] = path if path.is_absolute() else root / path
        return self.model_copy(update=updates)

    def required_data_directories(self) -> list[Path]:
        """Return the ordered list of required data directories."""
        resolved = self.resolve_paths()
        return [
            resolved.raw_data_path,
            resolved.processed_data_path,
            resolved.reference_data_path,
            resolved.export_path,
        ]

    def period_month_starts(self) -> list[date]:
        """Return the first day of each month in the configured period."""
        months: list[date] = []
        current = self.start_date.replace(day=1)
        last = self.end_date.replace(day=1)
        while current <= last:
            months.append(current)
            current = _add_months(current, 1)
        return months


def load_settings(
    profile_name: ProfileName | None = None,
    **overrides: object,
) -> AppSettings:
    """Load settings, optionally applying a named profile's defaults.

    Environment variables (`TRCI_*`) and `.env` still override defaults.
    Explicit ``overrides`` take highest precedence.

    Args:
        profile_name: Optional profile to apply before other overrides.
        **overrides: Explicit field overrides.

    Returns:
        Validated AppSettings instance with paths resolved to the repo root.
    """
    from src.config.profiles import get_profile_defaults

    values: dict[str, object] = {}
    if profile_name is not None:
        values.update(get_profile_defaults(profile_name))
    values.update({k: v for k, v in overrides.items() if v is not None})
    settings = AppSettings(**values)  # type: ignore[arg-type]
    return settings.resolve_paths()
