from __future__ import annotations

from pathlib import Path
from typing import Any
import re

from .change_detection import compute_fingerprint, normalize_metadata

DEFAULT_OUTPUT_PATH = Path("docs/generated/source-documentation.md")
FINGERPRINT_COMMENT = "<!-- documentation-fingerprint: {fingerprint} -->"
MISSING_METADATA = "Not available from the current source set"
UNCERTAIN_METADATA = "Uncertain or incomplete metadata"


def _stable_list(items: list[Any]) -> list[str]:
    normalized = [str(item).strip() for item in items if str(item).strip()]
    return sorted(normalized)


def _display_value(value: Any, fallback: str = MISSING_METADATA) -> str:
    if value is None:
        return fallback
    if isinstance(value, str):
        text = value.strip()
        return text if text else fallback
    if isinstance(value, (list, tuple)):
        items = [str(item).strip() for item in value if str(item).strip()]
        return ", ".join(sorted(items)) if items else fallback
    if isinstance(value, dict):
        if not value:
            return fallback
        return str(value)
    return str(value)


def _explicit_value(value: Any, *, field_name: str, missing_fields: list[str] | tuple[str, ...] | set[str] | None = None, uncertain_fields: list[str] | tuple[str, ...] | set[str] | None = None) -> str:
    missing = {str(item).strip() for item in (missing_fields or []) if str(item).strip()}
    uncertain = {str(item).strip() for item in (uncertain_fields or []) if str(item).strip()}

    if field_name in uncertain:
        return UNCERTAIN_METADATA
    if field_name in missing:
        return MISSING_METADATA

    return _display_value(value)


def _entity_name(item: Any) -> str:
    if isinstance(item, dict):
        name = item.get("name")
    else:
        name = getattr(item, "name", None)
    return str(name).strip() if name is not None else ""


def _entity_docstring(item: Any) -> Any:
    if isinstance(item, dict):
        return item.get("docstring")
    return getattr(item, "docstring", None)


def _named_entity_rows(items: list[Any], *, label: str, missing_fields: list[str], uncertain_fields: list[str]) -> list[str]:
    rows: list[str] = []
    for item in sorted(items, key=lambda entry: _entity_name(entry)):
        if not isinstance(item, dict) and not hasattr(item, "name"):
            continue
        name = _entity_name(item)
        if not name:
            continue
        field_name = f"{label.lower()}_docstring"
        docstring_value = _explicit_value(
            _entity_docstring(item),
            field_name=field_name,
            missing_fields=missing_fields,
            uncertain_fields=uncertain_fields,
        )
        rows.append(f"- {label} {name}: {docstring_value}")
    return rows


def _module_rows(module: dict[str, Any]) -> list[str]:
    missing_fields = [str(item).strip() for item in (module.get("missing_fields") or []) if str(item).strip()]
    uncertain_fields = [str(item).strip() for item in (module.get("uncertain_fields") or []) if str(item).strip()]
    rows: list[str] = []
    rows.append(f"### {module.get('module_name', 'module')}")
    rows.append(f"- Path: {_explicit_value(module.get('path'), field_name='path', missing_fields=missing_fields, uncertain_fields=uncertain_fields)}")
    rows.append(f"- Docstring: {_explicit_value(module.get('docstring'), field_name='docstring', missing_fields=missing_fields, uncertain_fields=uncertain_fields)}")
    rows.append(f"- Imports: {_explicit_value(module.get('imports'), field_name='imports', missing_fields=missing_fields, uncertain_fields=uncertain_fields)}")
    rows.append(f"- Classes: {_explicit_value(module.get('classes'), field_name='classes', missing_fields=missing_fields, uncertain_fields=uncertain_fields)}")
    rows.append(f"- Functions: {_explicit_value(module.get('functions'), field_name='functions', missing_fields=missing_fields, uncertain_fields=uncertain_fields)}")
    rows.extend(_named_entity_rows(module.get("classes") or [], label="Class", missing_fields=missing_fields, uncertain_fields=uncertain_fields))
    rows.extend(_named_entity_rows(module.get("functions") or [], label="Function", missing_fields=missing_fields, uncertain_fields=uncertain_fields))
    rows.append(f"- Missing fields: {', '.join(sorted(missing_fields)) if missing_fields else 'None'}")
    if uncertain_fields:
        rows.append(f"- Uncertain fields: {', '.join(sorted(uncertain_fields))}")
    rows.append("")
    return rows


def generate_markdown_documentation(metadata: dict[str, Any]) -> str:
    """Render a deterministic Markdown document from normalized documentation metadata."""
    normalized = normalize_metadata(metadata)
    modules = normalized.get("modules", [])
    if not isinstance(modules, list):
        modules = [modules] if modules else []
    module_entries = []
    for module in sorted(modules, key=lambda item: str(item.get("module_name", ""))):
        if isinstance(module, dict):
            module_entries.extend(_module_rows(module))

    module_summary = _display_value([module.get("module_name") for module in modules if isinstance(module, dict)], "None")
    class_names: list[str] = []
    function_names: list[str] = []
    for module in modules:
        if not isinstance(module, dict):
            continue
        class_names.extend(str(item.get("name", "")).strip() for item in (module.get("classes") or []) if str(item.get("name", "")).strip())
        function_names.extend(str(item.get("name", "")).strip() for item in (module.get("functions") or []) if str(item.get("name", "")).strip())

    summary_lines = [
        "# Repository Documentation",
        "",
        "## Summary",
        f"- Modules analyzed: {len(modules)}",
        f"- Classes found: {len(_stable_list(class_names))}",
        f"- Functions found: {len(_stable_list(function_names))}",
        f"- Module list: {module_summary}",
        "",
        "## Modules",
        "",
    ]
    if module_entries:
        summary_lines.extend(module_entries)
    else:
        summary_lines.append("No modules discovered from the current source set.")
        summary_lines.append("")

    fingerprint = compute_fingerprint(normalized)
    summary_lines.extend(["---", FINGERPRINT_COMMENT.format(fingerprint=fingerprint)])
    return "\n".join(summary_lines).rstrip() + "\n"


def needs_rewrite(existing_content: str | None, metadata: dict[str, Any]) -> bool:
    """Determine whether the current metadata differs materially from the last generated output."""
    if existing_content is None or not existing_content.strip():
        return True
    match = re.search(r"<!-- documentation-fingerprint: ([A-Fa-f0-9]+) -->\s*$", existing_content)
    if match is None:
        return True
    previous_fingerprint = match.group(1)
    current_fingerprint = compute_fingerprint(normalize_metadata(metadata))
    return previous_fingerprint != current_fingerprint


def write_generated_documentation(project_root: str | Path, metadata: dict[str, Any]) -> bool:
    """Write the generated documentation to the fixed output path only when content materially changes."""
    root = Path(project_root).expanduser().resolve()
    output_path = root / DEFAULT_OUTPUT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)

    existing_content = output_path.read_text(encoding="utf-8") if output_path.exists() else None
    rendered = generate_markdown_documentation(metadata)
    if not needs_rewrite(existing_content, metadata):
        return False

    output_path.write_text(rendered, encoding="utf-8")
    return True
