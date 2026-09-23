"""Dependency and package metadata extraction."""

from __future__ import annotations

import re
from pathlib import Path

from ..errors import ExtractionConfigError
from ..source_registry import is_authoritative_source

_FRAMEWORK_LABELS = {
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "pydantic": "Pydantic",
    "sqlalchemy": "SQLAlchemy",
}


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


def _dependency_name(value: str) -> str | None:
    candidate = value.strip().strip("\"'")
    candidate = candidate.split("#", 1)[0].strip()
    if not candidate or candidate.startswith("-"):
        return None
    candidate = re.split(r"[\s<>=!~\[;]", candidate, maxsplit=1)[0]
    if not candidate:
        return None
    return candidate


def _iter_dependency_values(content: str) -> list[str]:
    values: list[str] = []

    for line in content.splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        if cleaned.startswith("["):
            continue
        if cleaned.lower().startswith(("dependencies =", "install_requires =")):
            raw = cleaned.split("=", 1)[1].strip()
            values.extend(re.findall(r"['\"]([^'\"]+)['\"]", raw))
            continue
        if "=" in cleaned:
            key, remainder = cleaned.split("=", 1)
            if key.strip().lower() in {"dependencies", "install_requires"}:
                values.extend(re.findall(r"['\"]([^'\"]+)['\"]", remainder.strip()))
            continue
        dep_name = _dependency_name(cleaned)
        if dep_name:
            values.append(dep_name)

    return values


def extract_frameworks(repo_root: Path, files: list[str]) -> str | None:
    """Return authoritative framework names detected from project metadata."""
    framework_hits: list[str] = []
    seen: set[str] = set()

    for relative_path in files:
        if not relative_path.endswith(("pyproject.toml", "requirements.txt", "requirements-dev.txt", "setup.cfg", "setup.py")):
            continue
        content = _read_file_text(repo_root, relative_path)
        if not content:
            continue
        for dep in _iter_dependency_values(content):
            normalized = (_dependency_name(dep) or dep).lower().replace("_", "-")
            framework_name = None
            for key, label in _FRAMEWORK_LABELS.items():
                if normalized.startswith(key) or normalized.startswith(key.replace("-", "")):
                    framework_name = label
                    break
            if framework_name and framework_name not in seen:
                framework_hits.append(framework_name)
                seen.add(framework_name)

    return ", ".join(framework_hits) if framework_hits else None


def extract_upstream_dependencies(repo_root: Path, files: list[str]) -> str | None:
    """Return upstream project dependencies from authoritative config files."""
    dependency_names: list[str] = []
    seen: set[str] = set()

    for relative_path in files:
        if not relative_path.endswith(("pyproject.toml", "requirements.txt", "requirements-dev.txt", "setup.cfg", "setup.py")):
            continue
        content = _read_file_text(repo_root, relative_path)
        if not content:
            continue

        for value in _iter_dependency_values(content):
            dep_name = _dependency_name(value)
            if dep_name is None:
                continue
            lower_name = dep_name.lower()
            if lower_name in {"project", "build-system", "dependencies", "install_requires", "requires", "name", "version", "description", "requires-python", "setuptools", "wheel"}:
                continue
            if lower_name not in seen:
                dependency_names.append(dep_name)
                seen.add(lower_name)

    return ", ".join(dependency_names) if dependency_names else None


def extract_build_tool(repo_root: Path, files: list[str]) -> str | None:
    """Return the project build tool declared in authoritative config."""
    for relative_path in files:
        if relative_path.endswith("pyproject.toml"):
            content = _read_file_text(repo_root, relative_path)
            if "setuptools" in content.lower():
                return "setuptools"
            if "poetry" in content.lower():
                return "poetry"
            if "flit" in content.lower():
                return "flit"
    return None


def extract_current_version(repo_root: Path, files: list[str]) -> str | None:
    """Return the project version declared in authoritative config."""
    for relative_path in files:
        if relative_path.endswith("pyproject.toml"):
            content = _read_file_text(repo_root, relative_path)
            if "version =" in content:
                for line in content.splitlines():
                    if "version" in line and "=" in line:
                        value = line.split("=", 1)[1].strip().strip('"\'')
                        if value:
                            return value
    return None
