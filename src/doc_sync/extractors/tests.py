"""Testing and quality metadata extraction."""

from __future__ import annotations

from pathlib import Path

from ..errors import ExtractionConfigError
from ..source_registry import is_authoritative_source


def _read_file_text(repo_root: Path, relative_path: str) -> str:
    if not is_authoritative_source(relative_path):
        return ""
    file_path = repo_root / relative_path
    if not file_path.exists():
        return ""
    try:
        return file_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ExtractionConfigError(f"Unreadable authoritative file: {relative_path}") from exc


def extract_test_frameworks(repo_root: Path, files: list[str]) -> str | None:
    """Detect the test framework from technical configuration files."""
    for relative_path in files:
        content = _read_file_text(repo_root, relative_path)
        if not content:
            continue
        lowered = content.lower()
        if "pytest" in lowered:
            return "pytest"
    return None


def extract_code_coverage_goal(repo_root: Path, files: list[str]) -> str | None:
    """Return the declared coverage goal when it can be read from authoritative config."""
    for relative_path in files:
        if relative_path.endswith(("pyproject.toml", ".ini", ".cfg")):
            content = _read_file_text(repo_root, relative_path)
            if not content:
                continue
            if "cov" in content.lower() or "coverage" in content.lower():
                for line in content.splitlines():
                    lower = line.lower()
                    if "cov" in lower or "coverage" in lower:
                        value = line.split("=", 1)[1].strip().strip('"\'') if "=" in line else line.strip()
                        if value:
                            return value
    return None
