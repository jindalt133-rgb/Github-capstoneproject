from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from doc_sync.orchestrator import synchronize_manifest


FIXED_NOW = datetime(2026, 9, 21, 11, 22, 33, tzinfo=timezone.utc)


def _write_manifest(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_representative_repo_sync_matches_expected_manifest_snapshot(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "main.py").write_text(
        "import fastapi\nimport logging\napp = fastapi.FastAPI()\n",
        encoding="utf-8",
    )
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "name: CI\nrun: echo build\n",
        encoding="utf-8",
    )
    (repo / "Dockerfile").write_text("FROM python:3.11\n", encoding="utf-8")
    (repo / ".git").mkdir()
    (repo / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (repo / ".git" / "config").write_text(
        '[remote "origin"]\n\turl = https://github.com/acme/demo-platform.git\n',
        encoding="utf-8",
    )
    (repo / ".env").write_text("APP_ENV=production\nDB_PASSWORD=super-secret\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text(
        """[build-system]
requires = [\"setuptools>=68\"]
build-backend = \"setuptools.build_meta\"

[project]
name = \"demo-platform\"
version = \"2.4.1\"
requires-python = \">=3.11\"
dependencies = [\"fastapi\", \"pytest\", \"uvicorn\"]
""",
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
- Description: A demo API service.
- Language/Runtime: Python 3.10
- Frameworks: Django, Flask
- Primary Database: PostgreSQL
- Cloud Provider: AWS
- Infrastructure: Kubernetes
- Upstream Dependencies: older-lib
- Downstream Consumers: consumer-1
- External APIs: Payments API
- Main Branch: master
- Build Tool: poetry
- Critical Env Variables: DB_PASSWORD
- Deployment Pipeline: Azure Pipelines
- Test Frameworks: unittest
- Code Coverage Goal: 60%
- Security Scanning: Snyk
- Observation/Logging: Splunk
- GitHub Repository: https://github.com/example/legacy-app
- API Documentation: https://example.com/old-docs
- Current Version: 1.0.0
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- Last Updated: 2025-01-01T00:00:00Z
""",
    )

    result = synchronize_manifest(repo, manifest, now=FIXED_NOW)
    expected = (Path(__file__).with_name("expected_manifest.txt")).read_text(encoding="utf-8")

    assert result["status"] == "updated"
    assert result["changed"] is True
    assert result["updated_manifest"] == expected
    assert "DB_PASSWORD" not in result["updated_manifest"]
    assert "super-secret" not in result["updated_manifest"]
    assert "Service Owner: Jane Doe" in result["updated_manifest"]
    assert "Business Impact: Medium" in result["updated_manifest"]
    assert "Description: A demo API service." in result["updated_manifest"]
    assert "JIRA Board: TEAM-123" in result["updated_manifest"]
    assert "On-Call Rotation: Primary On-Call" in result["updated_manifest"]
    assert "Last Updated: 2026-09-21T11:22:33Z" in result["updated_manifest"]


def test_second_synchronization_produces_identical_manifest_without_churn(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "main.py").write_text(
        "import fastapi\nimport logging\napp = fastapi.FastAPI()\n",
        encoding="utf-8",
    )
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "name: CI\nrun: echo build\n",
        encoding="utf-8",
    )
    (repo / "Dockerfile").write_text("FROM python:3.11\n", encoding="utf-8")
    (repo / ".git").mkdir()
    (repo / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (repo / ".git" / "config").write_text(
        '[remote "origin"]\n\turl = https://github.com/acme/demo-platform.git\n',
        encoding="utf-8",
    )
    (repo / ".env").write_text("APP_ENV=production\nDB_PASSWORD=super-secret\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text(
        """[build-system]
requires = [\"setuptools>=68\"]
build-backend = \"setuptools.build_meta\"

[project]
name = \"demo-platform\"
version = \"2.4.1\"
requires-python = \">=3.11\"
dependencies = [\"fastapi\", \"pytest\", \"uvicorn\"]
""",
        encoding="utf-8",
    )

    manifest = repo / "docs" / "technical-app-manifest.md"
    synced_manifest = (Path(__file__).with_name("expected_manifest.txt")).read_text(encoding="utf-8")
    _write_manifest(manifest, synced_manifest)

    first = synchronize_manifest(repo, manifest, now=FIXED_NOW)
    second = synchronize_manifest(repo, manifest, now=FIXED_NOW)

    assert first["status"] == "no_drift"
    assert second["status"] == "no_drift"
    assert first["updated_manifest"] == second["updated_manifest"]
    assert first["updated_manifest"] == manifest.read_text(encoding="utf-8")
    assert "Last Updated: 2026-09-21T11:22:33Z" in first["updated_manifest"]
