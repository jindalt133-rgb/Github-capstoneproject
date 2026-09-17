"""Configuration constants for the technical manifest contract."""

MANIFEST_PATH = "docs/technical-app-manifest.md"
MISSING_VALUE = "Not Found"

# Explicitly identify the fields that must remain human-maintained.
PROTECTED_FIELDS = {
    "Service Owner": "Human-maintained field preserved by automation.",
    "Business Impact": "Human-maintained field preserved by automation.",
    "Description": "Human-maintained field preserved by automation.",
    "JIRA Board": "Human-maintained field preserved by automation.",
    "On-Call Rotation": "Human-maintained field preserved by automation.",
}

# Repository code and technical configuration are authoritative sources.
AUTHORITATIVE_SOURCE_ALLOWLIST = (
    "application code",
    "Python package and project configuration",
    "database configuration",
    "GitHub Actions workflow files",
    "pytest configuration and related test configuration",
    "other technical configuration files required to determine repository state",
)

NON_AUTHORITATIVE_SOURCES = (
    "README files",
    "narrative documentation",
    "general documentation",
)

# Sensitive values must never be stored as manifest metadata.
SENSITIVE_KEY_PATTERNS = (
    "SECRET",
    "PASSWORD",
    "TOKEN",
    "API_KEY",
    "CREDENTIAL",
    "PRIVATE_KEY",
)
