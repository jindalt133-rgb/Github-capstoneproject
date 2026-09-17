"""Configuration-driven extraction for database and operational metadata."""

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


def extract_database(repo_root: Path, files: list[str]) -> str | None:
    """Return the database in use when it is detectable from an authoritative config file."""
    for relative_path in files:
        content = _read_file_text(repo_root, relative_path)
        if not content:
            continue
        lowered = content.lower()
        if "sqlite" in lowered:
            return "SQLite"
        if "postgres" in lowered or "postgresql" in lowered:
            return "PostgreSQL"
        if "mysql" in lowered:
            return "MySQL"
    return None


def extract_critical_env_variables(repo_root: Path, files: list[str]) -> str | None:
    """Return env variable names without exposing secret values."""
    variable_names: list[str] = []
    seen: set[str] = set()

    for relative_path in files:
        if relative_path.endswith((".env", ".env.example", ".env.local")):
            content = _read_file_text(repo_root, relative_path)
            if not content:
                continue
            for line in content.splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    name = line.split("=", 1)[0].strip()
                    if name and name not in seen:
                        variable_names.append(name)
                        seen.add(name)

    return ", ".join(variable_names) if variable_names else None


def extract_main_branch(repo_root: Path, files: list[str]) -> str | None:
    """Return the repository default branch if it is available in git metadata."""
    git_head = repo_root / ".git" / "HEAD"
    if git_head.exists():
        try:
            branch_ref = git_head.read_text(encoding="utf-8").strip()
        except OSError:
            raise ValueError("Unreadable .git/HEAD metadata")
        if branch_ref.startswith("ref: refs/heads/"):
            return branch_ref.split("/", 3)[-1]
    return None


def extract_project_repository(repo_root: Path, files: list[str]) -> str | None:
    """Return the GitHub repository URL if available from git metadata."""
    git_config = repo_root / ".git" / "config"
    if git_config.exists():
        try:
            content = git_config.read_text(encoding="utf-8")
        except OSError:
            raise ValueError("Unreadable .git/config metadata")
        for line in content.splitlines():
            if "url =" in line.lower():
                url = line.split("=", 1)[1].strip()
                if url:
                    return url
    return None
