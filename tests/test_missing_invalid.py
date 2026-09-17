import pytest

from doc_sync.errors import ExtractionConfigError
from doc_sync.extractors import extract_repository_metadata


def test_missing_metadata_is_not_found(tmp_path):
    metadata = extract_repository_metadata(tmp_path)

    assert metadata["Application Name"] == "Not Found"
    assert metadata["Language/Runtime"] == "Not Found"
    assert metadata["Current Version"] == "Not Found"


def test_empty_technical_value_becomes_not_found(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = \"\"\nversion = \"\"\n", encoding="utf-8")

    metadata = extract_repository_metadata(tmp_path)

    assert metadata["Application Name"] == "Not Found"
    assert metadata["Current Version"] == "Not Found"


def test_readme_only_information_is_not_used_as_fallback(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\nFastAPI\n", encoding="utf-8")

    metadata = extract_repository_metadata(tmp_path)

    assert metadata["Frameworks"] == "Not Found"
    assert metadata["Language/Runtime"] == "Not Found"


def test_malformed_authoritative_configuration_raises_explicit_error(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project\nname = \"demo\"\n", encoding="utf-8")

    with pytest.raises(ExtractionConfigError, match="pyproject.toml"):
        extract_repository_metadata(tmp_path)


def test_unreadable_authoritative_source_is_not_treated_as_valid_metadata(tmp_path, monkeypatch):
    file_path = tmp_path / "pyproject.toml"
    file_path.write_text("[project]\nname = \"demo\"\n", encoding="utf-8")

    def raise_error(*args, **kwargs):
        raise OSError("Permission denied")

    monkeypatch.setattr(type(file_path), "read_text", raise_error)

    with pytest.raises(ExtractionConfigError):
        extract_repository_metadata(tmp_path)


def test_error_messages_do_not_expose_sensitive_values(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project\nname = \"demo\"\npassword = \"super-secret\"\n", encoding="utf-8")

    with pytest.raises(ExtractionConfigError, match="Malformed authoritative configuration file: pyproject.toml") as exc_info:
        extract_repository_metadata(tmp_path)

    assert "super-secret" not in str(exc_info.value)


def test_not_found_behavior_remains_unchanged(tmp_path):
    metadata = extract_repository_metadata(tmp_path)

    assert metadata["Application Name"] == "Not Found"
    assert metadata["Current Version"] == "Not Found"
    assert metadata["GitHub Repository"] == "Not Found"
