"""Deterministic normalization for repository-derived technical metadata."""

from __future__ import annotations

import re
from typing import Mapping
from urllib.parse import urlsplit, urlunsplit

from .field_catalog import FIELD_CATALOG

_NOT_FOUND = "Not Found"


def _normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def _canonicalize_runtime(value: str) -> str:
    mapping = {
        "python": "Python",
        "python3": "Python",
        "cpython": "Python",
        "node": "Node.js",
        "nodejs": "Node.js",
    }
    lowered = value.strip().lower()
    return mapping.get(lowered, value.strip())


def _normalize_case_for_field(field_name: str, value: str) -> str:
    mapping = {
        "Language/Runtime": _canonicalize_runtime,
        "Primary Database": {
            "sqlite": "SQLite",
            "postgres": "PostgreSQL",
            "postgresql": "PostgreSQL",
            "mysql": "MySQL",
        },
        "Cloud Provider": {
            "aws": "AWS",
            "azure": "Azure",
            "gcp": "GCP",
            "google cloud": "GCP",
        },
        "Build Tool": {
            "setuptools": "setuptools",
            "poetry": "poetry",
            "pip": "pip",
            "flit": "flit",
        },
        "Main Branch": {"main": "main", "master": "master"},
    }
    lookup = mapping.get(field_name)
    if isinstance(lookup, dict):
        lowered = value.strip().lower()
        return lookup.get(lowered, value.strip())
    if callable(lookup):
        return lookup(value)
    return value


def _normalize_list_value(value: str) -> str:
    raw = value.strip()
    if not raw:
        return raw

    cleaned: list[str] = []
    for segment in re.split(r"[,;|\n]+", raw):
        for chunk in re.split(r"\s+and\s+", segment):
            token = re.sub(r"\s+", " ", chunk).strip().strip("[]{}()")
            if token:
                cleaned.append(token)

    if not cleaned:
        return raw

    seen: set[str] = set()
    ordered: list[str] = []
    for item in sorted(cleaned, key=lambda item: item.lower()):
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(item)

    return ", ".join(ordered)


def _normalize_url(value: str) -> str:
    trimmed = value.strip()
    if not trimmed:
        return trimmed
    try:
        parts = urlsplit(trimmed)
    except ValueError:
        return trimmed

    if not parts.scheme and not parts.netloc:
        return trimmed

    scheme = parts.scheme.lower()
    netloc = parts.hostname.lower() if parts.hostname else ""
    if parts.port is not None:
        netloc = f"{netloc}:{parts.port}"
    path = parts.path.rstrip("/")
    if not path and netloc:
        path = ""
    return urlunsplit((scheme, netloc, path, parts.query, parts.fragment))


def _normalize_version(value: str) -> str:
    trimmed = value.strip()
    if not trimmed:
        return trimmed
    if trimmed.lower().startswith("v"):
        trimmed = trimmed[1:]
    return trimmed


def normalize_field_value(field_name: str, value: object) -> str:
    """Normalize a single metadata value according to the field contract rule."""
    if value is None:
        return _NOT_FOUND

    text = str(value)
    if text == _NOT_FOUND:
        return _NOT_FOUND

    rule = FIELD_CATALOG.get(field_name).normalization_rule.lower() if field_name in FIELD_CATALOG else ""

    if "list" in rule or "ordering" in rule or field_name in {
        "Frameworks",
        "Infrastructure",
        "Upstream Dependencies",
        "Downstream Consumers",
        "External APIs",
        "Critical Env Variables",
        "Test Frameworks",
        "Security Scanning",
        "Observation/Logging",
    }:
        normalized = _normalize_list_value(text)
    else:
        normalized = _normalize_whitespace(text)

    if "trim" in rule or "whitespace" in rule:
        normalized = _normalize_whitespace(normalized)
    if "case" in rule or field_name in {"Language/Runtime", "Primary Database", "Cloud Provider", "Build Tool"}:
        normalized = _normalize_case_for_field(field_name, normalized)
    if "url" in rule or field_name in {"GitHub Repository", "API Documentation"}:
        normalized = _normalize_url(normalized)
    if "version" in rule or field_name == "Current Version":
        normalized = _normalize_version(normalized)

    return normalized


def normalize_metadata(metadata: Mapping[str, object]) -> dict[str, str]:
    """Return a new dictionary with deterministic per-field normalization applied."""
    normalized: dict[str, str] = {}
    for field_name, value in metadata.items():
        normalized[field_name] = normalize_field_value(field_name, value)
    return normalized
