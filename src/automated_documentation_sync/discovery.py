from __future__ import annotations

from pathlib import Path

DEFAULT_EXCLUDED_DIR_NAMES = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "__pycache__",
    "tests",
    "build",
    "dist",
    "generated",
}


def _is_excluded(path: Path, project_root: Path) -> bool:
    relative_parts = path.relative_to(project_root).parts
    return any(part in DEFAULT_EXCLUDED_DIR_NAMES for part in relative_parts[:-1])


def discover_python_files(project_root: str | Path) -> list[Path]:
    """Return Python files under a project root while excluding default irrelevant directories."""
    root = Path(project_root).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Project root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Project root is not a directory: {root}")

    discovered: list[Path] = []
    for path in root.rglob("*.py"):
        if path.is_file() and not _is_excluded(path, root):
            discovered.append(path)

    return sorted(discovered, key=lambda item: str(item.relative_to(root)))
