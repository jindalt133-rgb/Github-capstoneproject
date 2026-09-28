from __future__ import annotations

from automated_documentation_sync.filtering import filter_sensitive_metadata, redact_sensitive_values


def test_redact_sensitive_values_removes_obvious_secret_like_values():
    sample = "api_key=abcd1234; token = SECRET_TOKEN; password: hunter2; bearer abc.def.ghi"

    result = redact_sensitive_values(sample)

    assert "abcd1234" not in result
    assert "SECRET_TOKEN" not in result
    assert "hunter2" not in result
    assert "abc.def.ghi" not in result
    assert "[REDACTED]" in result


def test_filter_sensitive_metadata_preserves_non_sensitive_data():
    metadata = {
        "project": "demo",
        "version": "1.2.3",
        "owner": "team-alpha",
        "notes": "safe summary",
    }

    result = filter_sensitive_metadata(metadata)

    assert result == metadata


def test_filter_sensitive_metadata_is_conservative_for_sensitive_keys():
    metadata = {
        "project": "demo",
        "api_key": "live-secret-key",
        "token": "abc123",
        "password": "super-secret",
        "owner": "keep me",
    }

    result = filter_sensitive_metadata(metadata)

    assert result["project"] == "demo"
    assert result["api_key"] == "[REDACTED]"
    assert result["token"] == "[REDACTED]"
    assert result["password"] == "[REDACTED]"
    assert result["owner"] == "keep me"
