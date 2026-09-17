from doc_sync.security import is_sensitive_key_name, sanitize_mapping, sanitize_value


def test_sensitive_environment_variable_names_are_detected():
    assert is_sensitive_key_name("DB_PASSWORD") is True
    assert is_sensitive_key_name("API_TOKEN") is True
    assert is_sensitive_key_name("AWS_SECRET_ACCESS_KEY") is True
    assert is_sensitive_key_name("PRIVATE_KEY") is True
    assert is_sensitive_key_name("CLIENT_SECRET") is True
    assert is_sensitive_key_name("AUTH_CREDENTIAL") is True
    assert is_sensitive_key_name("SECRET_KEY") is True


def test_detection_is_case_insensitive():
    assert is_sensitive_key_name("db_password") is True
    assert is_sensitive_key_name("api_token") is True
    assert is_sensitive_key_name("client_secret") is True
    assert is_sensitive_key_name("private_key") is True


def test_passwords_tokens_api_keys_private_keys_and_credentials_are_filtered():
    assert sanitize_value("DB_PASSWORD", "super-secret") == "Not Found"
    assert sanitize_value("API_TOKEN", "token-123") == "Not Found"
    assert sanitize_value("AWS_SECRET_ACCESS_KEY", "abc") == "Not Found"
    assert sanitize_value("PRIVATE_KEY", "-----BEGIN KEY-----") == "Not Found"
    assert sanitize_value("CLIENT_SECRET", "secret-value") == "Not Found"
    assert sanitize_value("AUTH_CREDENTIAL", "creds") == "Not Found"


def test_non_sensitive_technical_variables_are_retained():
    assert sanitize_value("APP_ENV", "production") == "production"
    assert sanitize_value("DATABASE_URL", "sqlite:///app.db") == "sqlite:///app.db"
    assert sanitize_value("ENDPOINT", "https://example.com") == "https://example.com"


def test_secret_values_are_never_returned():
    assert sanitize_value("DB_PASSWORD", "hunter2") != "hunter2"
    assert sanitize_value("API_KEY", "abc123") != "abc123"
    assert sanitize_value("PRIVATE_KEY", "top-secret") != "top-secret"


def test_not_found_remains_safe_and_unchanged():
    assert sanitize_value("DB_PASSWORD", "Not Found") == "Not Found"
    assert sanitize_mapping({"SECRET_KEY": "Not Found"}) == {"SECRET_KEY": "Not Found"}


def test_secret_values_do_not_appear_in_error_messages_or_output():
    result = sanitize_mapping({"API_KEY": "s3cr3t", "APP_ENV": "production"})
    assert result == {"API_KEY": "Not Found", "APP_ENV": "production"}
    assert "s3cr3t" not in str(result)
    assert "API_KEY" in result
