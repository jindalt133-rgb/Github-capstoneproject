from doc_sync.manifest import parse_manifest_fields, update_manifest_field, update_manifest_fields


SAMPLE_MANIFEST = """# Technical App Manifest

## Overview
- Application Name: demo-app
- Service Owner: Jane Doe
- Language/Runtime: Python 3.11

## Metadata
- Deployment Pipeline: GitHub Actions
- GitHub Repository: https://github.com/example/demo-app
"""


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


def test_update_manifest_field_rejects_protected_fields():
    try:
        update_manifest_field(SAMPLE_MANIFEST, "Service Owner", "New Owner")
        assert False, "Expected ValueError for protected field"
    except ValueError:
        pass


def test_update_manifest_field_handles_missing_value():
    updated = update_manifest_field(SAMPLE_MANIFEST, "GitHub Repository", None)
    assert "GitHub Repository: Not Found" in updated
