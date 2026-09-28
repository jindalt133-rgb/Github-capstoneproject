from __future__ import annotations

import hashlib
import json
from typing import Any


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _normalize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, dict):
        return {
            str(key): _normalize_value(item)
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, (list, tuple)):
        normalized_items = [_normalize_value(item) for item in value]
        return sorted(normalized_items, key=_stable_json)
    return str(value)


def normalize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Normalize documentation-relevant metadata into a deterministic structure."""
    return {
        str(key): _normalize_value(metadata[key])
        for key in sorted(metadata)
    }


def compute_fingerprint(metadata: dict[str, Any]) -> str:
    """Return a stable fingerprint for meaningful documentation metadata."""
    normalized = normalize_metadata(metadata)
    payload = _stable_json(normalized)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def has_meaningful_change(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    """Return True when documentation-relevant metadata changed in a meaningful way."""
    previous_norm = normalize_metadata(previous)
    current_norm = normalize_metadata(current)
    return previous_norm != current_norm
