from __future__ import annotations

import re

SENSITIVE_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd|pwd)\s*[:=]\s*['\"]?[^\s'\"]+"),
    re.compile(r"(?i)(bearer\s+[A-Za-z0-9._~+/-]+=*)"),
    re.compile(r"(?i)(aws[_-]?access[_-]?key[_-]?id|aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*['\"]?[^\s'\"]+"),
    re.compile(r"(?i)(connection[_-]?string|conn[_-]?string)\s*[:=]\s*['\"]?[^\s'\"]+"),
)


def redact_sensitive_values(text: str) -> str:
    """Remove or redact obvious secret-like values in a conservative manner."""
    sanitized = text
    for pattern in SENSITIVE_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    return sanitized


def filter_sensitive_metadata(values: dict[str, object]) -> dict[str, object]:
    """Return a filtered mapping while preserving non-sensitive metadata."""
    filtered: dict[str, object] = {}
    for key, value in values.items():
        if not isinstance(value, str):
            filtered[key] = value
            continue
        if _looks_sensitive_key(key):
            filtered[key] = "[REDACTED]"
            continue
        filtered[key] = redact_sensitive_values(value)
    return filtered


def _looks_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(marker in lowered for marker in ("token", "secret", "password", "passwd", "api_key", "apikey", "bearer", "connection_string"))
