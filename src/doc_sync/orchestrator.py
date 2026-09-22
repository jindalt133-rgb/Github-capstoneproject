"""Deterministic orchestration for manifest synchronization."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .config import MANIFEST_PATH
from .drift import detect_drift
from .extractors import extract_repository_metadata
from .manifest import (
    apply_last_updated_if_changed,
    find_manifest_field,
    parse_manifest_fields,
    update_manifest_fields,
)
from .normalize import normalize_metadata


def synchronize_manifest(
    repo_root: str | Path,
    manifest_path: str | Path = MANIFEST_PATH,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Compare repository metadata against the manifest and apply a safe, deterministic update when required."""
    repo_root_path = Path(repo_root)
    manifest_file = Path(manifest_path)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)

    repository_metadata = extract_repository_metadata(repo_root_path)
    normalized_repo = normalize_metadata(repository_metadata)

    if manifest_file.exists():
        manifest_text = manifest_file.read_text(encoding="utf-8")
    else:
        manifest_text = ""

    manifest_values = parse_manifest_fields(manifest_text)
    drift = detect_drift(normalized_repo, manifest_values)

    no_drift_result = {
        "status": "no_drift",
        "changed": False,
        "repo_root": str(repo_root_path),
        "manifest_path": str(manifest_file),
        "drifting_fields": (),
        "updated_fields": (),
        "manifest_text": manifest_text,
        "updated_manifest": manifest_text,
        "last_updated": manifest_values.get("Last Updated"),
    }

    if not drift["has_drift"]:
        return no_drift_result

    changed_fields = tuple(field for field in drift["drifting_fields"] if find_manifest_field(manifest_text, field) is not None)
    if not changed_fields:
        return {
            **no_drift_result,
            "status": "no_drift",
            "drifting_fields": (),
            "updated_fields": (),
            "updated_manifest": manifest_text,
            "last_updated": manifest_values.get("Last Updated"),
        }

    technical_updates = {
        field_name: normalized_repo.get(field_name, "Not Found")
        for field_name in changed_fields
    }
    updated_manifest = update_manifest_fields(manifest_text, technical_updates)
    updated_manifest = apply_last_updated_if_changed(updated_manifest, set(changed_fields), now=now)

    if manifest_file.exists() or manifest_text:
        manifest_file.write_text(updated_manifest, encoding="utf-8")

    return {
        "status": "updated",
        "changed": True,
        "repo_root": str(repo_root_path),
        "manifest_path": str(manifest_file),
        "drifting_fields": changed_fields,
        "updated_fields": changed_fields,
        "manifest_text": manifest_text,
        "updated_manifest": updated_manifest,
        "last_updated": parse_manifest_fields(updated_manifest).get("Last Updated"),
    }


__all__ = ["synchronize_manifest"]
