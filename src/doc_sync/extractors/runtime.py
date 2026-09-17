"""Runtime and application metadata extraction."""

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


def extract_language_runtime(repo_root: Path, files: list[str]) -> str | None:
    """Detect the interpreted runtime used by the repository."""
    for relative_path in files:
        if relative_path.endswith("pyproject.toml") or relative_path.endswith("requirements.txt"):
            content = _read_file_text(repo_root, relative_path)
            if not content:
                continue
            if "python_version" in content or "requires-python" in content:
                return "Python"
            if "fastapi" in content.lower() or "pytest" in content.lower():
                return "Python"
    if any(file.endswith(".py") for file in files):
        return "Python"
    return None


def extract_application_name(repo_root: Path, files: list[str]) -> str | None:
    """Detect the application name from authoritative project metadata."""
    for relative_path in files:
        if relative_path.endswith(("pyproject.toml", "setup.cfg")):
            content = _read_file_text(repo_root, relative_path)
            if not content:
                continue
            if "name =" in content:
                for line in content.splitlines():
                    candidate = line.strip()
                    if candidate.startswith("name") and "=" in candidate:
                        value = candidate.split("=", 1)[1].strip().strip('"\'')
                        if value:
                            return value
            if "name" in content.lower() and "=" in content:
                for line in content.splitlines():
                    if line.lower().startswith("name"):
                        value = line.split("=", 1)[1].strip().strip('"\'')
                        if value:
                            return value
    return None
