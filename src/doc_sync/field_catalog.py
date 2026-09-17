"""Catalog of repository-derived fields for the Technical-App-Manifest-v1."""

from __future__ import annotations

from .config import MISSING_VALUE, PROTECTED_FIELDS
from .models import FieldContract

REPOSITORY_DERIVED_FIELDS = (
    "Application Name",
    "Language/Runtime",
    "Frameworks",
    "Primary Database",
    "Cloud Provider",
    "Infrastructure",
    "Upstream Dependencies",
    "Downstream Consumers",
    "External APIs",
    "Main Branch",
    "Build Tool",
    "Critical Env Variables",
    "Deployment Pipeline",
    "Test Frameworks",
    "Code Coverage Goal",
    "Security Scanning",
    "Observation/Logging",
    "GitHub Repository",
    "API Documentation",
    "Current Version",
    "Last Updated",
)

# Human-maintained fields are explicitly preserved and not included in the repository-derived contract.
PROTECTED_MANIFEST_FIELDS = tuple(PROTECTED_FIELDS.keys())

FIELD_CATALOG = {
    "Application Name": FieldContract(
        manifest_field="Application Name",
        authoritative_source="application code and package metadata",
        extraction_method="read project metadata, application entrypoints, and package configuration",
        normalization_rule="trim whitespace and preserve canonical naming",
        fallback_behavior=MISSING_VALUE,
    ),
    "Language/Runtime": FieldContract(
        manifest_field="Language/Runtime",
        authoritative_source="Python package configuration and runtime config",
        extraction_method="parse Python project metadata or interpreter configuration",
        normalization_rule="normalize case and whitespace for runtime identifiers",
        fallback_behavior=MISSING_VALUE,
    ),
    "Frameworks": FieldContract(
        manifest_field="Frameworks",
        authoritative_source="Python package configuration and application dependencies",
        extraction_method="inspect declared dependencies and framework imports",
        normalization_rule="canonicalize list ordering and whitespace",
        fallback_behavior=MISSING_VALUE,
    ),
    "Primary Database": FieldContract(
        manifest_field="Primary Database",
        authoritative_source="database configuration and application settings",
        extraction_method="read database config and connection settings",
        normalization_rule="normalize database type names and whitespace",
        fallback_behavior=MISSING_VALUE,
    ),
    "Cloud Provider": FieldContract(
        manifest_field="Cloud Provider",
        authoritative_source="deployment configuration and infrastructure metadata",
        extraction_method="inspect provider metadata or deployment config",
        normalization_rule="normalize provider naming and whitespace",
        fallback_behavior=MISSING_VALUE,
    ),
    "Infrastructure": FieldContract(
        manifest_field="Infrastructure",
        authoritative_source="deployment and infrastructure configuration",
        extraction_method="read infrastructure config and workflow definitions",
        normalization_rule="normalize list formatting and whitespace",
        fallback_behavior=MISSING_VALUE,
    ),
    "Upstream Dependencies": FieldContract(
        manifest_field="Upstream Dependencies",
        authoritative_source="application code and dependency manifests",
        extraction_method="inspect package and service dependency declarations",
        normalization_rule="normalize list ordering and whitespace",
        fallback_behavior=MISSING_VALUE,
    ),
    "Downstream Consumers": FieldContract(
        manifest_field="Downstream Consumers",
        authoritative_source="technical configuration and integration definitions",
        extraction_method="detect consumer integration metadata from config and code",
        normalization_rule="normalize list ordering and whitespace",
        fallback_behavior=MISSING_VALUE,
    ),
    "External APIs": FieldContract(
        manifest_field="External APIs",
        authoritative_source="application config and integration code",
        extraction_method="inspect API client definitions and config values",
        normalization_rule="normalize service names, URLs, and whitespace",
        fallback_behavior=MISSING_VALUE,
    ),
    "Main Branch": FieldContract(
        manifest_field="Main Branch",
        authoritative_source="repository configuration and branch metadata",
        extraction_method="read repository guard or branch configuration",
        normalization_rule="trim whitespace and preserve canonical branch naming",
        fallback_behavior=MISSING_VALUE,
    ),
    "Build Tool": FieldContract(
        manifest_field="Build Tool",
        authoritative_source="Python project configuration and automation config",
        extraction_method="parse project build metadata and CI config",
        normalization_rule="normalize tool names and whitespace",
        fallback_behavior=MISSING_VALUE,
    ),
    "Critical Env Variables": FieldContract(
        manifest_field="Critical Env Variables",
        authoritative_source="environment configuration and deployment metadata",
        extraction_method="inspect env var declarations while filtering sensitive values",
        normalization_rule="normalize list ordering and omit sensitive values",
        fallback_behavior=MISSING_VALUE,
        sensitive=True,
    ),
    "Deployment Pipeline": FieldContract(
        manifest_field="Deployment Pipeline",
        authoritative_source="GitHub Actions workflow files",
        extraction_method="read workflow configuration and deployment stages",
        normalization_rule="normalize YAML values and whitespace",
        fallback_behavior=MISSING_VALUE,
    ),
    "Test Frameworks": FieldContract(
        manifest_field="Test Frameworks",
        authoritative_source="pytest config and testing setup",
        extraction_method="inspect testing configuration and test tooling files",
        normalization_rule="normalize list ordering and whitespace",
        fallback_behavior=MISSING_VALUE,
    ),
    "Code Coverage Goal": FieldContract(
        manifest_field="Code Coverage Goal",
        authoritative_source="test configuration and CI settings",
        extraction_method="read coverage threshold configuration",
        normalization_rule="normalize formatting and numeric values",
        fallback_behavior=MISSING_VALUE,
    ),
    "Security Scanning": FieldContract(
        manifest_field="Security Scanning",
        authoritative_source="repository automation and security config",
        extraction_method="inspect workflow and security tooling definitions",
        normalization_rule="normalize list ordering and whitespace",
        fallback_behavior=MISSING_VALUE,
    ),
    "Observation/Logging": FieldContract(
        manifest_field="Observation/Logging",
        authoritative_source="application and deployment configuration",
        extraction_method="read telemetry, monitoring, or logging configuration",
        normalization_rule="normalize list ordering and whitespace",
        fallback_behavior=MISSING_VALUE,
    ),
    "GitHub Repository": FieldContract(
        manifest_field="GitHub Repository",
        authoritative_source="repository metadata and remote configuration",
        extraction_method="read repository metadata or remote origin URL",
        normalization_rule="normalize URL formatting and whitespace",
        fallback_behavior=MISSING_VALUE,
    ),
    "API Documentation": FieldContract(
        manifest_field="API Documentation",
        authoritative_source="application config and documentation metadata",
        extraction_method="read config or generated docs references",
        normalization_rule="normalize URL and whitespace formatting",
        fallback_behavior=MISSING_VALUE,
    ),
    "Current Version": FieldContract(
        manifest_field="Current Version",
        authoritative_source="package metadata and release configuration",
        extraction_method="read project version metadata",
        normalization_rule="normalize version formatting and trim whitespace",
        fallback_behavior=MISSING_VALUE,
    ),
    "Last Updated": FieldContract(
        manifest_field="Last Updated",
        authoritative_source="synchronization operation, not repository-only metadata",
        extraction_method="managed by the synchronization process at runtime",
        normalization_rule="normalize to UTC ISO-8601 timestamp",
        fallback_behavior=MISSING_VALUE,
    ),
}

REQUIRED_MANIFEST_FIELDS = tuple(REPOSITORY_DERIVED_FIELDS)
