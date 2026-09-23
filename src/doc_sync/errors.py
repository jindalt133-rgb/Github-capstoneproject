"""Small errors for malformed or unreadable authoritative configuration."""

from __future__ import annotations

import configparser
import tomllib
from pathlib import Path

from .config import MISSING_VALUE
from .security import is_sensitive_key_name
from .source_registry import is_authoritative_source


class ExtractionConfigError(RuntimeError):
    """Raised when authoritative repository configuration cannot be read safely."""

    pass


def safe_value(value: object, *, key_name: object | None = None) -> str:
    """Return a safe fallback when a technical value is missing or sensitive."""
    if value is None:
        return MISSING_VALUE

    text = str(value).strip()
    if not text or text == MISSING_VALUE:
        return MISSING_VALUE

    if key_name is not None and is_sensitive_key_name(key_name):
        return MISSING_VALUE

    return text


def validate_authoritative_file(repo_root: Path, relative_path: str) -> None:
    """Validate that an authoritative config file can be read and parsed safely."""
    if not is_authoritative_source(relative_path):
        return

    file_path = repo_root / relative_path
    if not file_path.exists():
        return

    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ExtractionConfigError(f"Unreadable authoritative file: {relative_path}") from exc

    suffix = relative_path.lower()
    if suffix.endswith(".toml"):
        try:
            tomllib.loads(content)
        except tomllib.TOMLDecodeError as exc:
            raise ExtractionConfigError(f"Malformed authoritative configuration file: {relative_path}") from exc
        return

    if suffix.endswith((".ini", ".cfg")):
        parser = configparser.ConfigParser()
        try:
            parser.read_string(content)
        except configparser.Error as exc:
            raise ExtractionConfigError(f"Malformed authoritative configuration file: {relative_path}") from exc
        return

    if suffix.endswith((".yaml", ".yml")):
        try:
            import yaml  # type: ignore
        except ImportError:
            return
        try:
            yaml.safe_load(content)
        except (yaml.YAMLError, TypeError, ValueError) as exc:
            raise ExtractionConfigError(f"Malformed authoritative configuration file: {relative_path}") from exc
