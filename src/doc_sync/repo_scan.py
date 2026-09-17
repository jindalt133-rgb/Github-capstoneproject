"""Repository scanning helpers for authoritative technical sources."""

from __future__ import annotations

from pathlib import Path

from .source_registry import is_authoritative_source


def scan_repository_files(root: str | Path) -> list[str]:
    """Return a deterministic list of authoritative technical files under the repository root."""
    repo_root = Path(root)
    detected: list[str] = []

    if not repo_root.exists():
        return detected

    for candidate in sorted(repo_root.rglob("*")):
        if not candidate.is_file():
            continue

        relative_path = candidate.relative_to(repo_root).as_posix()
        if is_authoritative_source(relative_path):
            detected.append(relative_path)

    return detected
