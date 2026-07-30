"""Repository path utilities independent of the current working directory."""

from __future__ import annotations

from pathlib import Path

# Markers that identify the repository root when walking upward.
_ROOT_MARKERS: tuple[str, ...] = (
    "pyproject.toml",
    "implementation.md",
    "requirements.txt",
)


def get_repo_root(start: Path | None = None) -> Path:
    """Locate the repository root by walking upward from ``start``.

    Args:
        start: Starting path. Defaults to this file's location.

    Returns:
        Absolute path to the repository root.

    Raises:
        FileNotFoundError: If no known root marker is found.
    """
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if any((candidate / marker).exists() for marker in _ROOT_MARKERS):
            return candidate

    raise FileNotFoundError(
        "Unable to locate repository root. Expected one of: " + ", ".join(_ROOT_MARKERS)
    )


def ensure_directory(path: Path, *, exist_ok: bool = True) -> Path:
    """Create a directory if it does not exist.

    Args:
        path: Directory path to create.
        exist_ok: If False, raise when the directory already exists.

    Returns:
        The absolute directory path.
    """
    absolute = path.resolve()
    absolute.mkdir(parents=True, exist_ok=exist_ok)
    return absolute


def ensure_data_directories(directories: list[Path]) -> list[Path]:
    """Create each directory in ``directories`` if missing.

    Args:
        directories: Paths that must exist for generation and ETL.

    Returns:
        Absolute paths for each ensured directory.
    """
    return [ensure_directory(path) for path in directories]


def relative_to_repo(path: Path, repo_root: Path | None = None) -> Path:
    """Return ``path`` relative to the repository root when possible.

    Args:
        path: Absolute or relative path.
        repo_root: Optional explicit repository root.

    Returns:
        Path relative to the repo root, or the absolute path if unrelated.
    """
    root = repo_root or get_repo_root()
    absolute = path if path.is_absolute() else (root / path).resolve()
    try:
        return absolute.relative_to(root.resolve())
    except ValueError:
        return absolute
