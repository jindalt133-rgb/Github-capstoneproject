"""Simple allowlist/blocklist for authoritative technical repository sources."""

from __future__ import annotations

from pathlib import PurePosixPath

from .config import AUTHORITATIVE_SOURCE_ALLOWLIST, MANIFEST_PATH, NON_AUTHORITATIVE_SOURCES

_TECHNICAL_DIRECTORIES = (
    "src",
    "tests",
    ".github",
    "config",
    "infra",
    "deploy",
    "scripts",
    "migrations",
)

_TECHNICAL_FILE_NAMES = {
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "setup.py",
    "setup.cfg",
    "pytest.ini",
    "tox.ini",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "Procfile",
    "gunicorn.conf.py",
    ".env.example",
    ".python-version",
}

_TECHNICAL_EXTENSIONS = {".py", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".json"}
_GENERATED_ARTIFACT_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache"}


def _normalize_rel_path(path: str) -> str:
    return PurePosixPath(path.strip("/")) .as_posix()


def is_non_authoritative_source(path: str) -> bool:
    """Return True for documentation or narrative files that must not be treated as authoritative."""
    normalized = _normalize_rel_path(path)
    lower_name = PurePosixPath(normalized).name.lower()
    parts = PurePosixPath(normalized).parts

    if normalized == MANIFEST_PATH:
        return True

    if any(part.lower() == ".git" for part in parts):
        return True

    if any(part.lower() in _GENERATED_ARTIFACT_DIRS for part in parts):
        return True

    if any(part.lower().endswith(".egg-info") for part in parts):
        return True

    if any(part.lower() == "docs" for part in parts):
        return True

    if lower_name.startswith("readme"):
        return True

    if lower_name.endswith((".md", ".rst", ".txt")):
        return True

    if lower_name.endswith((".pyc", ".pyo")):
        return True

    for marker in NON_AUTHORITATIVE_SOURCES:
        if marker.lower() in normalized.lower():
            return True

    return False


def is_authoritative_source(path: str) -> bool:
    """Return True when a repository path is a valid technical source for metadata extraction."""
    normalized = _normalize_rel_path(path)
    if not normalized or normalized == ".":
        return False

    if is_non_authoritative_source(normalized):
        return False

    parts = PurePosixPath(normalized).parts
    lower_name = PurePosixPath(normalized).name.lower()

    if lower_name.endswith((".pyc", ".pyo")):
        return False

    if any(part.lower() == ".git" for part in parts):
        return False

    if any(part.lower() in _GENERATED_ARTIFACT_DIRS for part in parts):
        return False

    if any(part.lower().endswith(".egg-info") for part in parts):
        return False

    if lower_name in _TECHNICAL_FILE_NAMES:
        return True

    if any(part.lower() in _TECHNICAL_DIRECTORIES for part in parts):
        return True

    if lower_name.endswith(tuple(_TECHNICAL_EXTENSIONS)):
        return True

    if lower_name.endswith(":"):
        return False

    for marker in AUTHORITATIVE_SOURCE_ALLOWLIST:
        if marker.lower() in normalized.lower():
            return True

    return False
