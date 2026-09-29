from __future__ import annotations

from automated_documentation_sync.generation import (
    MISSING_METADATA,
    UNCERTAIN_METADATA,
    generate_markdown_documentation,
)


def test_missing_module_documentation_is_explicitly_reported():
    metadata = {
        "modules": [{
            "module_name": "sample",
            "path": "sample.py",
            "docstring": None,
            "imports": [],
            "classes": [],
            "functions": [],
            "missing_fields": ["docstring", "imports", "functions"],
            "uncertain_fields": [],
        }]
    }

    rendered = generate_markdown_documentation(metadata)

    assert MISSING_METADATA in rendered
    assert "- Docstring: Not available from the current source set" in rendered
    assert "- Missing fields: docstring, functions, imports" in rendered


def test_missing_function_or_class_documentation_is_explicitly_reported():
    metadata = {
        "modules": [{
            "module_name": "sample",
            "path": "sample.py",
            "docstring": "Example module.",
            "imports": ["import os"],
            "classes": [{"name": "Config", "docstring": None}],
            "functions": [{"name": "run", "docstring": None}],
            "missing_fields": ["class_docstring", "function_docstring"],
            "uncertain_fields": [],
        }]
    }

    rendered = generate_markdown_documentation(metadata)

    assert "Config" in rendered
    assert "run" in rendered
    assert MISSING_METADATA in rendered


def test_uncertain_or_incomplete_metadata_is_explicitly_reported():
    metadata = {
        "modules": [{
            "module_name": "sample",
            "path": "sample.py",
            "docstring": "Example module.",
            "imports": ["import os"],
            "classes": [],
            "functions": [],
            "missing_fields": [],
            "uncertain_fields": ["imports"],
        }]
    }

    rendered = generate_markdown_documentation(metadata)

    assert UNCERTAIN_METADATA in rendered
    assert "- Uncertain fields: imports" in rendered


def test_unavailable_information_is_not_fabricated():
    metadata = {
        "modules": [{
            "module_name": "sample",
            "path": "sample.py",
            "docstring": None,
            "imports": [],
            "classes": [],
            "functions": [],
            "missing_fields": ["docstring"],
            "uncertain_fields": [],
        }]
    }

    rendered = generate_markdown_documentation(metadata)

    assert "Not available from the current source set" in rendered
    assert "Unknown module purpose" not in rendered
    assert "N/A" not in rendered


def test_missing_and_uncertain_information_renders_deterministically():
    metadata = {
        "modules": [{
            "module_name": "sample",
            "path": "sample.py",
            "docstring": None,
            "imports": [],
            "classes": [],
            "functions": [],
            "missing_fields": ["docstring", "imports"],
            "uncertain_fields": ["functions"],
        }]
    }
    other = {
        "modules": [{
            "module_name": "sample",
            "path": "sample.py",
            "functions": [],
            "classes": [],
            "imports": [],
            "docstring": None,
            "missing_fields": ["imports", "docstring"],
            "uncertain_fields": ["functions"],
        }]
    }

    assert generate_markdown_documentation(metadata) == generate_markdown_documentation(other)
