import pytest

from doc_sync.manifest import parse_manifest_fields, update_manifest_field, update_manifest_fields


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
"""

PROTECTED_FIELDS = (
    "Service Owner",
    "Business Impact",
    "Description",
    "JIRA Board",
    "On-Call Rotation",
)


def test_parse_manifest_fields_reads_known_values():
    values = parse_manifest_fields(SAMPLE_MANIFEST)

    assert values["Application Name"] == "demo-app"
    assert values["Language/Runtime"] == "Python 3.11"
    assert values["Deployment Pipeline"] == "GitHub Actions"
    assert values["Service Owner"] == "Jane Doe"


def test_update_manifest_field_replaces_only_target_value():
    updated = update_manifest_field(SAMPLE_MANIFEST, "Application Name", "renamed-app")

    assert "Application Name: renamed-app" in updated
    assert "Service Owner: Jane Doe" in updated
    assert "Language/Runtime: Python 3.11" in updated
    assert "Deployment Pipeline: GitHub Actions" in updated


def test_update_manifest_fields_preserves_unrelated_content():
    updated = update_manifest_fields(
        SAMPLE_MANIFEST,
        {
            "Application Name": "final-app",
            "Deployment Pipeline": "Azure Pipelines",
        },
    )

    assert "# Technical App Manifest" in updated
    assert "## Overview" in updated
    assert "## Metadata" in updated
    assert "Application Name: final-app" in updated
    assert "Deployment Pipeline: Azure Pipelines" in updated
    assert "Service Owner: Jane Doe" in updated


@pytest.mark.parametrize("field_name", PROTECTED_FIELDS)
def test_each_protected_field_cannot_be_overwritten(field_name):
    original = SAMPLE_MANIFEST
    with pytest.raises(ValueError, match="Protected fields cannot be updated"):
        update_manifest_field(original, field_name, "new value")

    assert original == SAMPLE_MANIFEST
    assert f"{field_name}:" in original


def test_protected_field_updates_do_not_touch_unrelated_fields():
    original = SAMPLE_MANIFEST
    with pytest.raises(ValueError, match="Protected fields cannot be updated"):
        update_manifest_fields(
            original,
            {
                "Application Name": "replacement-app",
                "Service Owner": "New Owner",
                "Deployment Pipeline": "Azure Pipelines",
            },
        )

    assert original == SAMPLE_MANIFEST
    assert "Application Name: demo-app" in original
    assert "Deployment Pipeline: GitHub Actions" in original
    assert "Service Owner: Jane Doe" in original


def test_protected_field_with_empty_value_is_still_protected():
    manifest = SAMPLE_MANIFEST.replace("Jane Doe", "")
    with pytest.raises(ValueError, match="Protected fields cannot be updated"):
        update_manifest_field(manifest, "Service Owner", "")

    assert "Service Owner:" in manifest
    assert "Service Owner: " in manifest


def test_protected_field_enforcement_preserves_markdown_structure():
    original = SAMPLE_MANIFEST
    try:
        update_manifest_fields(
            original,
            {
                "Service Owner": "New Owner",
                "Application Name": "should-not-change",
            },
        )
        assert False, "Expected ValueError for protected field update"
    except ValueError:
        pass

    assert original == SAMPLE_MANIFEST
    assert "# Technical App Manifest" in original
    assert "## Overview" in original
    assert "## Metadata" in original


def test_update_manifest_field_handles_missing_value():
    updated = update_manifest_field(SAMPLE_MANIFEST, "GitHub Repository", None)
    assert "GitHub Repository: Not Found" in updated
