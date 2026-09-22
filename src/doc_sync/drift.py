"""Deterministic drift detection for repository-derived technical manifest fields."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .config import MISSING_VALUE, PROTECTED_FIELDS
from .field_catalog import REQUIRED_MANIFEST_FIELDS
from .manifest import parse_manifest_fields
from .normalize import normalize_field_value, normalize_metadata


def _normalize_comparable_manifest_values(values: Mapping[str, Any]) -> dict[str, str]:
    """Normalize manifest values according to the repository-derived field contract."""
    normalized: dict[str, str] = {}
    for field_name in REQUIRED_MANIFEST_FIELDS:
        if field_name in PROTECTED_FIELDS:
            continue

        raw_value = values.get(field_name, MISSING_VALUE)
        if raw_value is None:
            raw_value = MISSING_VALUE
        text_value = str(raw_value).strip()
        if text_value == "":
            text_value = MISSING_VALUE
        normalized[field_name] = normalize_field_value(field_name, text_value)
    return normalized


def compare_repository_and_manifest(
    repository_metadata: Mapping[str, Any],
    manifest_values: Mapping[str, Any],
) -> dict[str, Any]:
    """Compare repository metadata with the manifest and report any repository-derived technical drift."""
    filtered_repository = {
        field_name: value
        for field_name, value in repository_metadata.items()
        if field_name not in PROTECTED_FIELDS
    }
    normalized_repo = normalize_metadata(filtered_repository)
    normalized_manifest = _normalize_comparable_manifest_values(manifest_values)

    drifting_fields: list[str] = []
    for field_name in REQUIRED_MANIFEST_FIELDS:
        if field_name in PROTECTED_FIELDS or field_name == "Last Updated":
            continue

        repo_value = normalized_repo.get(field_name, MISSING_VALUE)
        manifest_value = normalized_manifest.get(field_name, MISSING_VALUE)
        if repo_value != manifest_value:
            drifting_fields.append(field_name)

    return {
        "has_drift": bool(drifting_fields),
        "drifting_fields": tuple(drifting_fields),
        "repository_values": normalized_repo,
        "manifest_values": normalized_manifest,
    }


def detect_drift(
    repository_metadata: Mapping[str, Any],
    manifest_values_or_text: Mapping[str, Any] | str,
) -> dict[str, Any]:
    """Detect drift between repository metadata and the current manifest representation."""
    if isinstance(manifest_values_or_text, str):
        manifest_values = parse_manifest_fields(manifest_values_or_text)
    else:
        manifest_values = dict(manifest_values_or_text)

    return compare_repository_and_manifest(repository_metadata, manifest_values)


def has_drift(repository_metadata: Mapping[str, Any], manifest_values_or_text: Mapping[str, Any] | str) -> bool:
    """Return True when repository-derived technical values differ from the manifest."""
    return detect_drift(repository_metadata, manifest_values_or_text)["has_drift"]


__all__ = [
    "compare_repository_and_manifest",
    "detect_drift",
    "has_drift",
]
