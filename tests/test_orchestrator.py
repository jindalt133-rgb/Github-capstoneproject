from datetime import datetime, timezone

import pytest

from doc_sync.errors import ExtractionConfigError
from doc_sync.orchestrator import synchronize_manifest


FIXED_NOW = datetime(2026, 9, 21, 11, 22, 33, tzinfo=timezone.utc)


def _write_manifest(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_synchronization_flow_updates_drifted_fields(tmp_path):
    repo = tmp_path / "repo"
    manifest = repo / "docs" / "technical-app-manifest.md"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "demo.py").write_text("print('demo')\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname = \"demo-app\"\nversion = \"1.0.0\"\n", encoding="utf-8")
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: old-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python 3.11

## Metadata
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: https://github.com/example/demo.git
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    result = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert result["status"] == "updated"
    assert result["changed"] is True
    assert "Application Name" in result["drifting_fields"]
    assert "GitHub Repository" in result["drifting_fields"]
    assert "Application Name: demo-app" in result["updated_manifest"]
    assert "GitHub Repository: Not Found" in result["updated_manifest"]
    assert "Last Updated: 2026-09-21T11:22:33Z" in result["updated_manifest"]
    assert "Service Owner: Jane Doe" in result["updated_manifest"]


def test_synchronization_flow_no_drift_returns_no_op(tmp_path):
    repo = tmp_path / "repo"
    manifest = repo / "docs" / "technical-app-manifest.md"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('demo')\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname = \"demo-app\"\n", encoding="utf-8")
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: demo-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python
- Deployment Pipeline: Not Found
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: Not Found
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    result = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert result["status"] == "no_drift"
    assert result["changed"] is False
    assert result["updated_manifest"] == result["manifest_text"]
    assert result["last_updated"] == "2025-01-01T00:00:00Z"


def test_multiple_technical_fields_drift_are_reported(tmp_path):
    repo = tmp_path / "repo"
    manifest = repo / "docs" / "technical-app-manifest.md"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "demo.py").write_text("print('demo')\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname = \"demo-app\"\nversion = \"2.0.0\"\n", encoding="utf-8")
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: old-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python 3.11

## Metadata
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: Not Found
- Current Version: 1.0.0
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    result = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert result["changed"] is True
    assert "Application Name" in result["drifting_fields"]
    assert "Current Version" in result["drifting_fields"]
    assert "Last Updated: 2026-09-21T11:22:33Z" in result["updated_manifest"]


def test_protected_fields_remain_unchanged_during_sync(tmp_path):
    repo = tmp_path / "repo"
    manifest = repo / "docs" / "technical-app-manifest.md"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "demo.py").write_text("print('demo')\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname = \"demo-app\"\n", encoding="utf-8")
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: old-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: Not Found
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    result = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert result["status"] == "updated"
    assert "Application Name: demo-app" in result["updated_manifest"]
    assert "GitHub Repository: Not Found" in result["updated_manifest"]
    assert "Service Owner: Jane Doe" in result["updated_manifest"]
    assert "Description: Example summary." in result["updated_manifest"]


def test_last_updated_changes_only_when_real_technical_update_occurs(tmp_path):
    repo = tmp_path / "repo"
    manifest = repo / "docs" / "technical-app-manifest.md"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "demo.py").write_text("print('demo')\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname = \"demo-app\"\n", encoding="utf-8")
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: demo-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python
- Deployment Pipeline: Not Found
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: Not Found
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    result = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert result["status"] == "no_drift"
    assert result["changed"] is False
    assert "Last Updated: 2025-01-01T00:00:00Z" in result["manifest_text"]


def test_repeated_synchronization_becomes_no_op_after_sync(tmp_path):
    repo = tmp_path / "repo"
    manifest = repo / "docs" / "technical-app-manifest.md"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "demo.py").write_text("print('demo')\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname = \"demo-app\"\n", encoding="utf-8")
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: old-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: Not Found
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    first = synchronize_manifest(repo, manifest, now=FIXED_NOW)
    second = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert first["changed"] is True
    assert second["status"] == "no_drift"
    assert second["updated_manifest"] == second["manifest_text"]


def test_missing_technical_metadata_becomes_not_found(tmp_path):
    repo = tmp_path / "repo"
    manifest = repo / "docs" / "technical-app-manifest.md"
    repo.mkdir()
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: demo-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: https://github.com/example/demo.git
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    result = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert result["status"] == "updated"
    assert result["changed"] is True
    assert "GitHub Repository" in result["drifting_fields"]
    assert "GitHub Repository: Not Found" in result["updated_manifest"]


def test_authoritative_source_parsing_failure_prevents_partial_update(tmp_path):
    repo = tmp_path / "repo"
    manifest = repo / "docs" / "technical-app-manifest.md"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project\nname = \"broken\"\n", encoding="utf-8")
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: old-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: Not Found
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    with pytest.raises(ExtractionConfigError):
        synchronize_manifest(repo, manifest, now=FIXED_NOW)

    manifest_text = manifest.read_text(encoding="utf-8")
    assert "Application Name: old-app" in manifest_text
    assert "Last Updated: 2025-01-01T00:00:00Z" in manifest_text


def test_sensitive_values_never_appear_in_output(tmp_path):
    repo = tmp_path / "repo"
    manifest = repo / "docs" / "technical-app-manifest.md"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "main.py").write_text("PASSWORD = 'not-secret'\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname = \"demo-app\"\n", encoding="utf-8")
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: old-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: Not Found
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    result = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert "not-secret" not in result["updated_manifest"]
    assert "PASSWORD" not in result["updated_manifest"]


def test_unrelated_manifest_content_remains_unchanged(tmp_path):
    repo = tmp_path / "repo"
    manifest = repo / "docs" / "technical-app-manifest.md"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "demo.py").write_text("print('demo')\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname = \"demo-app\"\n", encoding="utf-8")
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: old-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python

This is narrative content that must be preserved.

## Metadata
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: Not Found
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    result = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert "This is narrative content that must be preserved." in result["updated_manifest"]
    assert "## Overview" in result["updated_manifest"]
    assert "## Metadata" in result["updated_manifest"]
    assert "Service Owner: Jane Doe" in result["updated_manifest"]
