from doc_sync.config import MISSING_VALUE, PROTECTED_FIELDS, SENSITIVE_KEY_PATTERNS
from doc_sync.field_catalog import FIELD_CATALOG, PROTECTED_MANIFEST_FIELDS, REQUIRED_MANIFEST_FIELDS


def test_catalog_has_structural_contracts():
    assert isinstance(FIELD_CATALOG, dict)
    assert len(FIELD_CATALOG) > 0

    for field_name in REQUIRED_MANIFEST_FIELDS:
        contract = FIELD_CATALOG[field_name]
        assert contract.manifest_field == field_name
        assert contract.authoritative_source
        assert contract.extraction_method
        assert contract.normalization_rule
        assert contract.fallback_behavior == MISSING_VALUE


def test_required_repository_fields_are_registered():
    expected_fields = {
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
    }

    assert set(REQUIRED_MANIFEST_FIELDS) == expected_fields
    assert all(field in FIELD_CATALOG for field in REQUIRED_MANIFEST_FIELDS)


def test_protected_fields_are_registered():
    expected_protected = {
        "Service Owner",
        "Business Impact",
        "Description",
        "JIRA Board",
        "On-Call Rotation",
    }

    assert set(PROTECTED_FIELDS) == expected_protected
    assert set(PROTECTED_MANIFEST_FIELDS) == expected_protected
    assert all(field in FIELD_CATALOG for field in REQUIRED_MANIFEST_FIELDS)


def test_missing_values_use_not_found_fallback():
    for field_name in REQUIRED_MANIFEST_FIELDS:
        assert FIELD_CATALOG[field_name].fallback_behavior == MISSING_VALUE


def test_sensitive_patterns_are_registered():
    expected_sensitive = {
        "SECRET",
        "PASSWORD",
        "TOKEN",
        "API_KEY",
        "CREDENTIAL",
        "PRIVATE_KEY",
    }

    assert set(SENSITIVE_KEY_PATTERNS) == expected_sensitive
    for pattern in expected_sensitive:
        assert pattern in SENSITIVE_KEY_PATTERNS
