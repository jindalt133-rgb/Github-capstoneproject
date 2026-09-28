from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_OUTPUT_PATH = Path("docs/generated/source-documentation.md")


def resolve_project_root(project_root: str | None) -> Path:
    """Resolve the project root and validate it is a directory."""
    root = Path(project_root).expanduser() if project_root is not None else Path.cwd()
    if not root.exists():
        raise FileNotFoundError(f"Project root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Project root is not a directory: {root}")
    return root.resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Synchronize generated repository documentation from Python source files."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Path to the repository root to analyze.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        project_root = resolve_project_root(args.project_root)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    output_path = project_root / DEFAULT_OUTPUT_PATH
    relative_output_path = output_path.relative_to(project_root)
    print(f"Project root: {project_root}")
    print(f"Output path: {str(relative_output_path).replace('\\', '/')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
