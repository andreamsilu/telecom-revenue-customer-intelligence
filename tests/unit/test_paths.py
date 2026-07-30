"""Unit tests for repository path utilities."""

from __future__ import annotations

from pathlib import Path

from src.config import load_settings
from src.utils.paths import (
    ensure_data_directories,
    get_repo_root,
    relative_to_repo,
)


def test_get_repo_root_finds_markers() -> None:
    """Repository root is detected via known marker files."""
    root = get_repo_root()
    assert (root / "pyproject.toml").exists()
    assert (root / "implementation.md").exists()
    assert root.is_absolute()


def test_paths_resolve_relative_to_repo_root() -> None:
    """Configured data paths resolve against the repository root."""
    root = get_repo_root()
    settings = load_settings(profile_name="development")

    assert settings.raw_data_path == root / "data" / "raw"
    assert settings.processed_data_path == root / "data" / "processed"
    assert settings.reference_data_path == root / "data" / "reference"
    assert settings.export_path == root / "data" / "exports"
    assert settings.raw_data_path.is_absolute()


def test_required_directories_can_be_identified() -> None:
    """Required data directories are listed and can be created."""
    settings = load_settings(profile_name="development")
    directories = settings.required_data_directories()
    assert len(directories) == 4

    ensured = ensure_data_directories(directories)
    for path in ensured:
        assert path.exists()
        assert path.is_dir()


def test_relative_to_repo() -> None:
    """Absolute paths inside the repo can be expressed relatively."""
    root = get_repo_root()
    relative = relative_to_repo(root / "data" / "raw")
    assert relative == Path("data") / "raw"
