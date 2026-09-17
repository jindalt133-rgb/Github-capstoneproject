"""Repository metadata extraction by technical domain."""

from __future__ import annotations

from pathlib import Path

from ..errors import ExtractionConfigError, validate_authoritative_file
from ..field_catalog import FIELD_CATALOG
from ..repo_scan import scan_repository_files
from .config import (
    extract_critical_env_variables,
    extract_database,
    extract_main_branch,
    extract_project_repository,
)
from .deps import (
    extract_build_tool,
    extract_current_version,
    extract_frameworks,
    extract_upstream_dependencies,
)
from .runtime import extract_application_name, extract_language_runtime
from .tests import extract_code_coverage_goal, extract_test_frameworks
from .workflows import (
    extract_api_documentation,
    extract_cloud_provider,
    extract_deployment_pipeline,
    extract_infrastructure,
    extract_security_scanning,
    extract_observation_logging,
)


class ExtractionError(RuntimeError):
    """Raised when an authoritative repository config is unreadable or malformed."""


def _fallback(value: str | None) -> str:
    return value if value and value.strip() else "Not Found"


def _extract_field_value(field_name: str, repo_root: Path, files: list[str]) -> str:
    if field_name == "Application Name":
        return _fallback(extract_application_name(repo_root, files))
    if field_name == "Language/Runtime":
        return _fallback(extract_language_runtime(repo_root, files))
    if field_name == "Frameworks":
        return _fallback(extract_frameworks(repo_root, files))
    if field_name == "Primary Database":
        return _fallback(extract_database(repo_root, files))
    if field_name == "Cloud Provider":
        return _fallback(extract_cloud_provider(repo_root, files))
    if field_name == "Infrastructure":
        return _fallback(extract_infrastructure(repo_root, files))
    if field_name == "Upstream Dependencies":
        return _fallback(extract_upstream_dependencies(repo_root, files))
    if field_name == "Downstream Consumers":
        return "Not Found"
    if field_name == "External APIs":
        return "Not Found"
    if field_name == "Main Branch":
        return _fallback(extract_main_branch(repo_root, files))
    if field_name == "Build Tool":
        return _fallback(extract_build_tool(repo_root, files))
    if field_name == "Critical Env Variables":
        return _fallback(extract_critical_env_variables(repo_root, files))
    if field_name == "Deployment Pipeline":
        return _fallback(extract_deployment_pipeline(repo_root, files))
    if field_name == "Test Frameworks":
        return _fallback(extract_test_frameworks(repo_root, files))
    if field_name == "Code Coverage Goal":
        return _fallback(extract_code_coverage_goal(repo_root, files))
    if field_name == "Security Scanning":
        return _fallback(extract_security_scanning(repo_root, files))
    if field_name == "Observation/Logging":
        return _fallback(extract_observation_logging(repo_root, files))
    if field_name == "GitHub Repository":
        return _fallback(extract_project_repository(repo_root, files))
    if field_name == "API Documentation":
        return _fallback(extract_api_documentation(repo_root, files))
    if field_name == "Current Version":
        return _fallback(extract_current_version(repo_root, files))
    if field_name == "Last Updated":
        return "Not Found"
    return "Not Found"


def extract_repository_metadata(root: str | Path) -> dict[str, str]:
    """Extract raw repository-derived technical metadata from authoritative sources."""
    repo_root = Path(root)
    files = scan_repository_files(repo_root)
    metadata: dict[str, str] = {}

    for relative_path in files:
        validate_authoritative_file(repo_root, relative_path)

    for field_name in FIELD_CATALOG:
        if field_name == "Last Updated":
            continue
        metadata[field_name] = _extract_field_value(field_name, repo_root, files)

    return metadata
