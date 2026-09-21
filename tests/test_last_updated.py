from datetime import datetime, timezone

import pytest

from doc_sync.manifest import (
    apply_last_updated_if_changed,
    generate_utc_iso8601_timestamp,
    update_last_updated_field,
)


FIXED_NOW = datetime(2026, 9, 21, 11, 22, 33, tzinfo=timezone.utc)

SAMPLE_MANIFEST = """# Technical App Manifest

## Overview
- Application Name: demo-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: A task management API.
- Language/Runtime: Python 3.11

## Metadata
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: https://github.com/example/demo-app
- Last Updated: 2025-01-01T00:00:00Z
"""


def test_generate_utc_iso8601_timestamp():
    timestamp = generate_utc_iso8601_timestamp(FIXED_NOW)

    assert timestamp == "2026-09-21T11:22:33Z"


def test_last_updated_changes_when_real_technical_update_occurs():
    updated = apply_last_updated_if_changed(SAMPLE_MANIFEST, {"Application Name": "demo-app-v2"}, now=FIXED_NOW)

    assert "Last Updated: 2026-09-21T11:22:33Z" in updated
    assert "Application Name: demo-app-v2" in updated


def test_last_updated_does_not_change_on_no_drift():
    original = SAMPLE_MANIFEST
    updated = apply_last_updated_if_changed(original, set(), now=FIXED_NOW)

    assert updated == original
    assert "Last Updated: 2025-01-01T00:00:00Z" in updated


def test_last_updated_does_not_change_for_protected_field_only_changes():
    original = SAMPLE_MANIFEST
    updated = apply_last_updated_if_changed(original, {"Service Owner": "Jane Smith"}, now=FIXED_NOW)

    assert updated == original
    assert "Last Updated: 2025-01-01T00:00:00Z" in updated
    assert "Service Owner: Jane Doe" in updated


def test_existing_last_updated_value_is_preserved_when_no_synchronization_change_occurs():
    updated = apply_last_updated_if_changed(SAMPLE_MANIFEST, set(), now=FIXED_NOW)

    assert "Last Updated: 2025-01-01T00:00:00Z" in updated
    assert "Last Updated: 2026-09-21T11:22:33Z" not in updated


def test_timestamp_format_is_valid_iso8601_utc():
    timestamp = generate_utc_iso8601_timestamp(FIXED_NOW)

    assert timestamp.endswith("Z")
    assert len(timestamp) == 20
    assert timestamp[4] == "-" and timestamp[7] == "-"
    assert timestamp[10] == "T" and timestamp[13] == ":" and timestamp[16] == ":"


def test_unrelated_manifest_content_remains_unchanged():
    updated = apply_last_updated_if_changed(SAMPLE_MANIFEST, {"Deployment Pipeline": "Azure Pipelines"}, now=FIXED_NOW)

    assert "# Technical App Manifest" in updated
    assert "## Overview" in updated
    assert "## Metadata" in updated
    assert "Service Owner: Jane Doe" in updated
    assert "Business Impact: Medium" in updated
    assert "Description: A task management API." in updated
    assert "JIRA Board: TEAM-123" in updated
    assert "Last Updated: 2026-09-21T11:22:33Z" in updated
