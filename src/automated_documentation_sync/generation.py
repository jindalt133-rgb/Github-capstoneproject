from __future__ import annotations

from pathlib import Path
from typing import Any
import re

from .change_detection import compute_fingerprint, normalize_metadata

DEFAULT_OUTPUT_PATH = Path("docs/generated/source-documentation.md")
FINGERPRINT_COMMENT = "<!-- documentation-fingerprint: {fingerprint} -->"


def _stable_list(items: list[Any]) -> list[str]:
    normalized = [str(item).strip() for item in items if str(item).strip()]
    return sorted(normalized)


def _display_value(value: Any, fallback: str = "Not available from the current source set") -> str:
    if value is None:
        return fallback
    if isinstance(value, str):
        text = value.strip()
        return text if text else fallback
    if isinstance(value, (list, tuple)):
        items = [str(item).strip() for item in value if str(item).strip()]
        return ", ".join(items) if items else fallback
    return str(value)


def _module_rows(module: dict[str, Any]) -> list[str]:
    rows: list[str] = []
    rows.append(f"### {module.get('module_name', 'module')}")
    rows.append(f"- Path: {_display_value(module.get('path'))}")
    rows.append(f"- Docstring: {_display_value(module.get('docstring'))}")
    rows.append(f"- Imports: {_display_value(module.get('imports'))}")
    rows.append(f"- Classes: {_display_value(module.get('classes', []), 'None')}")
    rows.append(f"- Functions: {_display_value(module.get('functions', []), 'None')}")
    missing_fields = module.get("missing_fields") or []
    if missing_fields:
        rows.append(f"- Missing fields: {_display_value(missing_fields, 'None')}")
    else:
        rows.append("- Missing fields: None")
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
