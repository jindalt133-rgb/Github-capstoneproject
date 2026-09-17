from doc_sync.normalize import normalize_field_value, normalize_metadata


def test_whitespace_normalization():
    assert normalize_field_value("Application Name", "  demo app  ") == "demo app"
    assert normalize_field_value("Main Branch", "  main   ") == "main"


def test_case_normalization_for_runtime_and_database():
    assert normalize_field_value("Language/Runtime", " python ") == "Python"
    assert normalize_field_value("Primary Database", "postgresql") == "PostgreSQL"
    assert normalize_field_value("Cloud Provider", " azure ") == "Azure"


def test_list_normalization_and_deterministic_ordering():
    payload = {"Frameworks": "fastapi, Flask ; django\npytest", "Upstream Dependencies": "zeta, alpha and beta"}
    normalized = normalize_metadata(payload)

    assert normalized["Frameworks"] == "django, fastapi, Flask, pytest"
    assert normalized["Upstream Dependencies"] == "alpha, beta, zeta"


def test_url_normalization():
    assert normalize_field_value("GitHub Repository", " https://GitHub.com/Example/demo.git/ ") == "https://github.com/Example/demo.git"
    assert normalize_field_value("API Documentation", "https://example.com/docs/") == "https://example.com/docs"


def test_version_normalization():
    assert normalize_field_value("Current Version", " v1.2.3 ") == "1.2.3"
    assert normalize_field_value("Current Version", "1.2.3") == "1.2.3"


def test_not_found_remains_exact():
    assert normalize_field_value("Application Name", "Not Found") == "Not Found"
    assert normalize_field_value("GitHub Repository", None) == "Not Found"


def test_meaningful_values_are_preserved():
    assert normalize_field_value("Build Tool", "setuptools") == "setuptools"
    assert normalize_field_value("Main Branch", "release/v1") == "release/v1"
    assert normalize_field_value("Application Name", "Demo-App") == "Demo-App"


def test_determinism_same_input_same_output():
    value = "  fastapi, Flask ; django\npytest  "
    assert normalize_field_value("Frameworks", value) == normalize_field_value("Frameworks", value)
    assert normalize_field_value("GitHub Repository", "https://example.com/repo") == "https://example.com/repo"
