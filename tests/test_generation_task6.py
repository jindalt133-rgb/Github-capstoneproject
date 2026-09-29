from __future__ import annotations

from automated_documentation_sync.generation import (
    DEFAULT_OUTPUT_PATH,
    generate_markdown_documentation,
    needs_rewrite,
    write_generated_documentation,
)


def test_generate_markdown_documentation_is_deterministic_for_equivalent_metadata():
    metadata = {
        "modules": [
            {
                "module_name": "sample",
                "path": "sample.py",
                "docstring": "Example module.",
                "imports": ["import os", "from pathlib import Path"],
                "classes": [{"name": "Config", "methods": ["load", "save"]}],
                "functions": [{"name": "run", "returns": "str"}],
                "missing_fields": [],
            }
        ]
    }
    other = {
        "modules": [
            {
                "module_name": "sample",
                "path": "sample.py",
                "docstring": "Example module.",
                "imports": ["from pathlib import Path", "import os"],
                "classes": [{"name": "Config", "methods": ["save", "load"]}],
                "functions": [{"name": "run", "returns": "str"}],
                "missing_fields": [],
            }
        ]
    }

    first = generate_markdown_documentation(metadata)
    second = generate_markdown_documentation(other)

    assert first == second
    assert "# Repository Documentation" in first
    assert "## Summary" in first
    assert "## Modules" in first


def test_needs_rewrite_ignores_equivalent_content():
    metadata = {
        "modules": [{
            "module_name": "sample",
            "path": "sample.py",
            "docstring": "Example module.",
            "imports": ["import os"],
            "classes": [],
            "functions": [{"name": "run", "returns": "str"}],
            "missing_fields": [],
        }]
    }
    rendered = generate_markdown_documentation(metadata)

    assert needs_rewrite(rendered, metadata) is False


def test_needs_rewrite_detects_meaningful_documentation_change():
    previous = {
        "modules": [{
            "module_name": "sample",
            "path": "sample.py",
            "docstring": "Example module.",
            "functions": [{"name": "run", "returns": "str"}],
            "missing_fields": [],
        }]
    }
    current = {
        "modules": [{
            "module_name": "sample",
            "path": "sample.py",
            "docstring": "Example module.",
            "functions": [{"name": "run", "returns": "int"}],
            "missing_fields": [],
        }]
    }

    assert needs_rewrite(generate_markdown_documentation(previous), current) is True


def test_write_generated_documentation_uses_fixed_output_path_and_keeps_generated_output_separate(tmp_path):
    project_root = tmp_path
    metadata = {
        "modules": [{
            "module_name": "sample",
            "path": "sample.py",
            "docstring": "Example module.",
            "imports": ["import os"],
            "classes": [],
            "functions": [{"name": "run", "returns": "str"}],
            "missing_fields": [],
        }]
    }

    output_path = project_root / DEFAULT_OUTPUT_PATH

    assert write_generated_documentation(project_root, metadata) is True
    assert output_path.exists()
    assert "# Repository Documentation" in output_path.read_text(encoding="utf-8")
    assert "documentation-fingerprint:" in output_path.read_text(encoding="utf-8")
