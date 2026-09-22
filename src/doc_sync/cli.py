"""Manual CLI entrypoint for repository-to-manifest synchronization."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import MANIFEST_PATH
from .orchestrator import synchronize_manifest


def build_parser() -> argparse.ArgumentParser:
    """Create the minimal CLI parser for manual synchronization runs."""
    parser = argparse.ArgumentParser(description="Synchronize repository-derived technical metadata into the manifest.")
    parser.add_argument(
        "repo_root",
        nargs="?",
        default=".",
        help="Repository root to inspect (default: current working directory).",
    )
    parser.add_argument(
        "--manifest-path",
        default=MANIFEST_PATH,
        help="Path to the manifest file relative to the repository root or as an absolute path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run manual synchronization for the current repository."""
    parser = build_parser()
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest_path)
    if not manifest_path.is_absolute():
        manifest_path = repo_root / manifest_path
    manifest_path = manifest_path.resolve()

    try:
        result = synchronize_manifest(repo_root, manifest_path)
    except Exception as exc:  # pragma: no cover - exercised via CLI tests
        print(f"Synchronization failed: {exc}", file=sys.stderr)
        return 1

    if result["status"] == "updated":
        fields = ", ".join(result["drifting_fields"]) if result["drifting_fields"] else "technical metadata"
        print(f"Synchronization complete: updated {fields}.")
        print(f"Manifest: {result['manifest_path']}")
        print(f"Last Updated: {result['last_updated']}")
        return 0

    print("No drift detected. Manifest already up to date.")
    print(f"Manifest: {result['manifest_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
