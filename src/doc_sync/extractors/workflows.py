"""Workflow and pipeline metadata extraction."""

from __future__ import annotations

import re
from pathlib import Path

from ..source_registry import is_authoritative_source


def _read_file_text(repo_root: Path, relative_path: str) -> str:
    if not is_authoritative_source(relative_path):
        return ""
    file_path = repo_root / relative_path
    if not file_path.exists():
        return ""
    try:
        return file_path.read_text(encoding="utf-8")
    except OSError:
        raise ValueError(f"Unreadable authoritative file: {relative_path}")


def extract_deployment_pipeline(repo_root: Path, files: list[str]) -> str | None:
    """Detect workflow-based deployment pipelines declared in GitHub Actions files."""
    workflow_names: set[str] = set()
    for relative_path in files:
        if relative_path.endswith((".yml", ".yaml")) and ".github/workflows" in relative_path:
            workflow_names.add("GitHub Actions")
            content = _read_file_text(repo_root, relative_path)
            if "deploy" in content.lower() or "release" in content.lower():
                workflow_names.add("Deployment")
    return ", ".join(sorted(workflow_names)) if workflow_names else None


def extract_security_scanning(repo_root: Path, files: list[str]) -> str | None:
    """Return security scanning tools detected in authoritative config or workflow files."""
    tool_names: set[str] = set()
    for relative_path in files:
        if relative_path.endswith((".yml", ".yaml", ".toml", ".ini")):
            content = _read_file_text(repo_root, relative_path)
            if "bandit" in content.lower():
                tool_names.add("Bandit")
            if "safety" in content.lower():
                tool_names.add("Safety")
            if "trivy" in content.lower():
                tool_names.add("Trivy")
            if "security" in content.lower() and "scan" in content.lower():
                tool_names.add("Security Scan")
    return ", ".join(sorted(tool_names)) if tool_names else None


def extract_cloud_provider(repo_root: Path, files: list[str]) -> str | None:
    """Detect the cloud provider from authoritative deployment config or workflow files."""
    for relative_path in files:
        content = _read_file_text(repo_root, relative_path)
        if not content:
            continue
        lowered = content.lower()
        if "azure" in lowered:
            return "Azure"
        if "aws" in lowered:
            return "AWS"
        if "gcp" in lowered or "google cloud" in lowered:
            return "GCP"
    return None


def extract_infrastructure(repo_root: Path, files: list[str]) -> str | None:
    """Detect infrastructure markers that reflect runtime or deployment infrastructure."""
    for relative_path in files:
        if relative_path.endswith(("Dockerfile", "docker-compose.yml", "docker-compose.yaml")):
            return "Docker"
        content = _read_file_text(repo_root, relative_path)
        if "kubernetes" in content.lower():
            return "Kubernetes"
    return None


def extract_api_documentation(repo_root: Path, files: list[str]) -> str | None:
    """Find API documentation references in authoritative config or application code."""
    for relative_path in files:
        if relative_path.endswith((".py", ".toml", ".yml", ".yaml")):
            content = _read_file_text(repo_root, relative_path)
            if not content:
                continue
            if "swagger" in content.lower() or "redoc" in content.lower() or "/docs" in content.lower():
                return "Swagger/OpenAPI"
    return None


def extract_observation_logging(repo_root: Path, files: list[str]) -> str | None:
    """Return logging or observability tooling when detected in authoritative config."""
    for relative_path in files:
        if relative_path.endswith((".py", ".yml", ".yaml", ".toml")):
            content = _read_file_text(repo_root, relative_path)
            if not content:
                continue
            if "logging" in content.lower() or "observability" in content.lower() or "opentelemetry" in content.lower():
                return "Logging / Observability"
    return None
