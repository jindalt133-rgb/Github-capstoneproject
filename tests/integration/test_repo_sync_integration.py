from __future__ import annotations

from datetime import datetime, timezone

import pytest

from doc_sync.errors import ExtractionConfigError
from doc_sync.orchestrator import synchronize_manifest

FIXED_NOW = datetime(2026, 9, 21, 11, 22, 33, tzinfo=timezone.utc)


def _write_manifest(path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_repo_with_defaults(repo_root):
    (repo_root / "src").mkdir(parents=True, exist_ok=True)
    (repo_root / "src" / "main.py").write_text("print('demo')\n", encoding="utf-8")
    (repo_root / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (repo_root / ".github" / "workflows" / "ci.yml").write_text(
        "name: CI\nrun: echo build\n",
        encoding="utf-8",
    )
    (repo_root / "pyproject.toml").write_text(
        """
[project]
name = \"demo-api\"
version = \"1.2.3\"
dependencies = [\"fastapi\", \"pytest\"]
requires-python = \">=3.11\"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return repo_root


def test_synchronization_updates_drifted_metadata_and_preserves_human_fields(tmp_path):
    repo = _build_repo_with_defaults(tmp_path / "repo")
    manifest = repo / "docs" / "technical-app-manifest.md"
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: legacy-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python 3.10

## Metadata
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: https://github.com/example/legacy-app
- Current Version: 0.9.0
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    result = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert result["status"] == "updated"
    assert result["changed"] is True
    assert "Application Name" in result["drifting_fields"]
    assert "Current Version" in result["drifting_fields"]
    assert "GitHub Repository" in result["drifting_fields"]
    assert "Application Name: demo-api" in result["updated_manifest"]
    assert "Current Version: 1.2.3" in result["updated_manifest"]
    assert "Language/Runtime: Python" in result["updated_manifest"]
    assert "Service Owner: Jane Doe" in result["updated_manifest"]
    assert "Description: Example summary." in result["updated_manifest"]
    assert "JIRA Board: TEAM-123" in result["updated_manifest"]
    assert "Last Updated: 2026-09-21T11:22:33Z" in result["updated_manifest"]


def test_no_drift_leaves_manifest_unchanged_and_keeps_last_updated_stable(tmp_path):
    repo = _build_repo_with_defaults(tmp_path / "repo")
    manifest = repo / "docs" / "technical-app-manifest.md"
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: demo-api
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: Not Found
- Current Version: 1.2.3
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    result = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert result["status"] == "no_drift"
    assert result["changed"] is False
    assert result["updated_manifest"] == result["manifest_text"]
    assert result["last_updated"] == "2025-01-01T00:00:00Z"
    assert manifest.read_text(encoding="utf-8") == result["manifest_text"]


def test_missing_repository_metadata_updates_to_not_found(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest = repo / "docs" / "technical-app-manifest.md"
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: demo-api
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: https://github.com/example/demo-api
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    result = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert result["status"] == "updated"
    assert result["changed"] is True
    assert "GitHub Repository" in result["drifting_fields"]
    assert "GitHub Repository: Not Found" in result["updated_manifest"]
    assert "Last Updated: 2026-09-21T11:22:33Z" in result["updated_manifest"]


def test_sensitive_values_are_never_written_to_manifest_and_protected_fields_stay_intact(tmp_path):
    repo = _build_repo_with_defaults(tmp_path / "repo")
    (repo / ".env").write_text(
        "DB_PASSWORD=super-secret\nAPI_TOKEN=token-123\nAPP_ENV=production\n",
        encoding="utf-8",
    )
    manifest = repo / "docs" / "technical-app-manifest.md"
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: legacy-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python 3.10
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: Not Found
- Critical Env Variables: APP_ENV
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    result = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    manifest_text = result["updated_manifest"]
    assert "super-secret" not in manifest_text
    assert "token-123" not in manifest_text
    assert "DB_PASSWORD" not in manifest_text
    assert "API_TOKEN" not in manifest_text
    assert "Service Owner: Jane Doe" in manifest_text
    assert "Business Impact: Medium" in manifest_text
    assert "Description: Example summary." in manifest_text
    assert "JIRA Board: TEAM-123" in manifest_text
    assert "On-Call Rotation: Primary On-Call" in manifest_text


def test_malformed_authoritative_config_aborts_without_partial_manifest_write(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project\nname = \"broken-app\"\n", encoding="utf-8")
    manifest = repo / "docs" / "technical-app-manifest.md"
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

    with pytest.raises(ExtractionConfigError, match="pyproject.toml"):
        synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert manifest.read_text(encoding="utf-8") == """# Technical App Manifest

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
"""


def test_idempotent_second_run_does_not_change_last_updated(tmp_path):
    repo = _build_repo_with_defaults(tmp_path / "repo")
    manifest = repo / "docs" / "technical-app-manifest.md"
    _write_manifest(
        manifest,
        """# Technical App Manifest

## Overview
- Application Name: legacy-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python 3.10
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: Not Found
- Current Version: 0.9.0
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    first = synchronize_manifest(repo, manifest, now=FIXED_NOW)
    second = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert first["status"] == "updated"
    assert first["changed"] is True
    assert second["status"] == "no_drift"
    assert second["changed"] is False
    assert "Last Updated: 2026-09-21T11:22:33Z" in first["updated_manifest"]
    assert second["manifest_text"] == second["updated_manifest"]
    assert second["last_updated"] == "2026-09-21T11:22:33Z"
