"""Dependency and package metadata extraction."""

from __future__ import annotations

import re
from pathlib import Path

from ..source_registry import is_authoritative_source


def _read_file_text(repo_root: Path, relative_path: str) -> str:
    if not is_authoritative_source(relative_path):
        return ""
    file_path = repo_root / relative_path
    if not file_path.exists():
        return ""
    try:
        return file_path.read_text(encoding="utf-8")
    except OSError:
        raise ValueError(f"Unreadable authoritative file: {relative_path}")


def extract_frameworks(repo_root: Path, files: list[str]) -> str | None:
    """Return authoritative framework names detected from project metadata."""
    framework_hits: list[str] = []
    seen: set[str] = set()

    for relative_path in files:
        content = _read_file_text(repo_root, relative_path)
        if not content:
            continue

        lowered = content.lower()
        for framework in ("fastapi", "flask", "django", "pydantic", "sqlalchemy"):
            if framework in lowered and framework not in seen:
                framework_hits.append(framework.title())
                seen.add(framework)

        if "fastapi" in lowered:
            framework_hits.append("FastAPI")
            seen.add("fastapi")

    return ", ".join(framework_hits) if framework_hits else None


def extract_upstream_dependencies(repo_root: Path, files: list[str]) -> str | None:
    """Return upstream project dependencies from authoritative config files."""
    dependency_names: list[str] = []
    seen: set[str] = set()

    for relative_path in files:
        if not relative_path.endswith(("pyproject.toml", "requirements.txt", "requirements-dev.txt", "setup.cfg")):
            continue
        content = _read_file_text(repo_root, relative_path)
        if not content:
            continue

        for line in content.splitlines():
            cleaned = line.strip()
            if not cleaned or cleaned.startswith("#"):
                continue

            if "dependencies" in cleaned.lower() and "=" in cleaned:
                serialized = cleaned.split("=", 1)[1].strip()
                values = re.findall(r"['\"]([^'\"]+)['\"]", serialized)
                if values:
                    for value in values:
                        if value and value not in seen:
                            dependency_names.append(value)
                            seen.add(value)
                    continue

            if cleaned.startswith("["):
                continue

            match = re.match(r"([A-Za-z0-9_.-]+)", cleaned)
            if match:
                value = match.group(1)
                if value.lower() not in {"project", "dependencies", "pytest", "build-system", "install_requires"} and value not in seen:
                    dependency_names.append(value)
                    seen.add(value)

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
