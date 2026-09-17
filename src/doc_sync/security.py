"""Small, practical filtering for sensitive repository values."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from .config import MISSING_VALUE, SENSITIVE_KEY_PATTERNS


def _normalize_key_name(name: Any) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", str(name)).strip("_").upper()


def is_sensitive_key_name(name: Any) -> bool:
    """Return True when a key name matches an approved sensitive pattern."""
    if name is None:
        return False

    normalized = _normalize_key_name(name)
    if not normalized:
        return False

    for pattern in SENSITIVE_KEY_PATTERNS:
        if pattern and pattern.upper() in normalized:
            return True
    return False


def sanitize_value(key_name: Any, value: Any) -> str:
    """Return a safe representation for repository-derived technical values."""
    if value is None:
        return MISSING_VALUE

    text = str(value).strip()
    if text == MISSING_VALUE:
        return MISSING_VALUE

    if is_sensitive_key_name(key_name):
        return MISSING_VALUE

    return text


def sanitize_mapping(mapping: Mapping[str, Any]) -> dict[str, str]:
    """Redact secret-like keys while preserving non-sensitive configuration entries."""
    sanitized: dict[str, str] = {}

    for key, value in mapping.items():
        key_name = str(key)
        if is_sensitive_key_name(key_name):
            sanitized[key_name] = MISSING_VALUE
            continue

        sanitized[key_name] = sanitize_value(key_name, value)

    return sanitized


def require_safe_value(key_name: Any, value: Any) -> str:
    """Raise only when a sensitive value is detected, without exposing the secret itself."""
    if is_sensitive_key_name(key_name):
        raise ValueError(f"Sensitive configuration field '{str(key_name)}' is not permitted.")
    return sanitize_value(key_name, value)
