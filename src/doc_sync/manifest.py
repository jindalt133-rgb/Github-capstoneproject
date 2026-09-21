"""Manifest parsing and safe field-level Markdown updates for repository-derived technical metadata."""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

from .config import MANIFEST_PATH, MISSING_VALUE, PROTECTED_FIELDS
from .field_catalog import FIELD_CATALOG, REQUIRED_MANIFEST_FIELDS
from .security import sanitize_value


def _manifest_field_names() -> tuple[str, ...]:
    """Return all manifest labels that may appear in the template, including protected human fields."""
    return REQUIRED_MANIFEST_FIELDS + tuple(PROTECTED_FIELDS)


def find_manifest_field(manifest_text: str, field_name: str) -> int | None:
    """Return the line number for an existing manifest field label, or None when absent."""
    field_label = field_name.strip()
    patterns = [
        rf"^\s*(?:[-*]\s+)?(?:\*\*)?{re.escape(field_label)}(?:\*\*)?\s*:\s*.*$",
        rf"^\s*(?:[-*]\s+)?{re.escape(field_label)}\s*[-:]\s*.*$",
    ]

    for index, line in enumerate(manifest_text.splitlines()):
        for pattern in patterns:
            if re.match(pattern, line):
                return index
    return None


def parse_manifest_fields(manifest_text: str) -> dict[str, str]:
    """Return the currently captured manifest field values keyed by their field labels."""
    found: dict[str, str] = {}
    for field_name in _manifest_field_names():
        index = find_manifest_field(manifest_text, field_name)
        if index is None:
            continue
        lines = manifest_text.splitlines()
        match = re.search(rf"^(?:\s*(?:[-*]\s+)?(?:\*\*)?{re.escape(field_name)}(?:\*\*)?\s*[:\-]\s*)(.*)$", lines[index])
        if match:
            found[field_name] = match.group(1).strip()
    return found


def _is_allowed_technical_field(field_name: str) -> bool:
    return field_name in FIELD_CATALOG or field_name in REQUIRED_MANIFEST_FIELDS


def validate_update_request(field_names: Iterable[str]) -> None:
    """Reject protected field requests before any manifest mutation occurs."""
    protected_fields = [field_name for field_name in field_names if field_name in PROTECTED_FIELDS]
    if protected_fields:
        raise ValueError(f"Protected fields cannot be updated: {', '.join(protected_fields)}")


def generate_utc_iso8601_timestamp(now: datetime | None = None) -> str:
    """Return a UTC ISO-8601 timestamp string for manifest synchronization events."""
    timestamp = now or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    utc_time = timestamp.astimezone(timezone.utc)
    return utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")


def update_manifest_field(manifest_text: str, field_name: str, value: object) -> str:
    """Update a single manifest field while preserving all other Markdown content."""
    validate_update_request([field_name])

    if not _is_allowed_technical_field(field_name):
        raise ValueError(f"Unsupported manifest field: {field_name}")

    safe_value = sanitize_value(field_name, value)
    if safe_value == "":
        safe_value = MISSING_VALUE
    if safe_value is None:
        safe_value = MISSING_VALUE

    lines = manifest_text.splitlines()
    matched = False

    for index, line in enumerate(lines):
        patterns = [
            rf"^(\s*(?:[-*]\s+)?(?:\*\*)?){re.escape(field_name)}(?:\*\*)?(\s*:\s*)(.*)$",
            rf"^(\s*(?:[-*]\s+)?){re.escape(field_name)}(\s*[-:]\s*)(.*)$",
        ]
        for pattern in patterns:
            match = re.match(pattern, line)
            if not match:
                continue
            prefix, sep, _ = match.groups()
            lines[index] = f"{prefix}{field_name}{sep}{safe_value}"
            matched = True
            break
        if matched:
            break

    if not matched:
        raise ValueError(f"Manifest field not found: {field_name}")

    return "\n".join(lines) + ("\n" if manifest_text.endswith("\n") else "")


def update_last_updated_field(manifest_text: str, value: str | None = None, *, now: datetime | None = None) -> str:
    """Update the Last Updated field while preserving unrelated Markdown content."""
    timestamp = value if value is not None else generate_utc_iso8601_timestamp(now)
    return update_manifest_field(manifest_text, "Last Updated", timestamp)


def apply_last_updated_if_changed(manifest_text: str, changed_fields: Iterable[str] | dict[str, object] | set[str], *, now: datetime | None = None) -> str:
    """Apply real technical updates and stamp Last Updated only when the manifest actually changes."""
    if isinstance(changed_fields, dict):
        updates = dict(changed_fields)
        field_keys = tuple(updates.keys())
    else:
        updates = {}
        field_keys = tuple(changed_fields)

    if not field_keys:
        return manifest_text

    protected_updates = [field for field in field_keys if field in PROTECTED_FIELDS]
    if protected_updates and len(protected_updates) == len(field_keys):
        return manifest_text

    if updates:
        technical_updates = {field: value for field, value in updates.items() if field not in PROTECTED_FIELDS}
        if not technical_updates:
            return manifest_text
        updated_manifest = update_manifest_fields(manifest_text, technical_updates)
        return update_last_updated_field(updated_manifest, now=now)

    technical_fields = [field for field in field_keys if field not in PROTECTED_FIELDS]
    if not technical_fields:
        return manifest_text

    return update_last_updated_field(manifest_text, now=now)


def update_manifest_fields(manifest_text: str, field_values: dict[str, object]) -> str:
    """Update multiple repository-derived technical fields while preserving all non-target content."""
    validate_update_request(field_values)

    updated = manifest_text
    for field_name, value in field_values.items():
        updated = update_manifest_field(updated, field_name, value)
    return updated


def update_manifest_file(path: str | Path, field_values: dict[str, object]) -> str:
    """Read a manifest file, apply the allowed field updates, and write the result back."""
    target_path = Path(path)
    text = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
    updated = update_manifest_fields(text, field_values)
    target_path.write_text(updated, encoding="utf-8")
    return updated


__all__ = [
    "MANIFEST_PATH",
    "find_manifest_field",
    "parse_manifest_fields",
    "generate_utc_iso8601_timestamp",
    "update_manifest_field",
    "update_manifest_fields",
    "update_last_updated_field",
    "apply_last_updated_if_changed",
    "update_manifest_file",
]
