from __future__ import annotations

from automated_documentation_sync.change_detection import (
    compute_fingerprint,
    has_meaningful_change,
    normalize_metadata,
)


def test_identical_metadata_is_unchanged():
    metadata = {
        "module_name": "sample",
        "docstring": "Example module.",
        "imports": ["import os", "from pathlib import Path"],
        "classes": [{"name": "Config", "methods": ["load", "save"]}],
        "functions": [{"name": "run", "returns": "str"}],
    }

    assert has_meaningful_change(metadata, metadata) is False


def test_equivalent_normalized_metadata_is_unchanged():
    previous = {
        "module_name": "sample",
        "docstring": " Example module. ",
        "imports": ["from pathlib import Path", "import os"],
        "classes": [{"name": "Config", "methods": ["save", "load"]}],
        "functions": [{"name": "run", "returns": "str"}],
    }
    current = {
        "module_name": "sample",
        "docstring": "Example module.",
        "imports": ["import os", "from pathlib import Path"],
        "classes": [{"name": "Config", "methods": ["load", "save"]}],
        "functions": [{"name": "run", "returns": "str"}],
    }

    assert normalize_metadata(previous) == normalize_metadata(current)
    assert has_meaningful_change(previous, current) is False


def test_documentation_relevant_metadata_change_is_detected():
    previous = {
        "module_name": "sample",
        "docstring": "Example module.",
        "functions": [{"name": "run", "returns": "str"}],
    }
    current = {
        "module_name": "sample",
        "docstring": "Example module.",
        "functions": [{"name": "run", "returns": "int"}],
    }

    assert has_meaningful_change(previous, current) is True


def test_comparison_fingerprint_is_deterministic():
    metadata = {
        "module_name": "sample",
        "docstring": "Example module.",
        "imports": ["import os", "from pathlib import Path"],
        "classes": [{"name": "Config", "methods": ["load", "save"]}],
        "functions": [{"name": "run", "returns": "str"}],
    }

    first = compute_fingerprint(metadata)
    second = compute_fingerprint({
        "functions": [{"name": "run", "returns": "str"}],
        "imports": ["from pathlib import Path", "import os"],
        "classes": [{"name": "Config", "methods": ["save", "load"]}],
        "module_name": "sample",
        "docstring": "Example module.",
    })

    assert first == second
