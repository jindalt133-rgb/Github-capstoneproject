from __future__ import annotations

from pathlib import Path

from automated_documentation_sync.analysis import analyze_python_source


def test_analyze_python_source_extracts_metadata_without_executing(tmp_path):
    source_dir = tmp_path / "pkg"
    source_dir.mkdir()
    source_file = source_dir / "services.py"
    source_file.write_text(
        '''"""Service module."""\n\nimport os\nfrom typing import Any\n\nclass Worker:\n    """Worker class."""\n\n    def run(self, value: str) -> str:\n        return value\n\ndef build_service() -> str:\n    return "ready"\n''',
        encoding="utf-8",
    )

    result = analyze_python_source(source_file, project_root=tmp_path)

    assert result.module_name == "services"
    assert result.docstring == "Service module."
    assert len(result.imports) == 2
    assert [cls.name for cls in result.classes] == ["Worker"]
    assert [fn.name for fn in result.functions] == ["build_service"]
    assert result.missing_fields == []


def test_analyze_python_source_reports_missing_metadata_explicitly(tmp_path):
    source_file = tmp_path / "empty_module.py"
    source_file.write_text("x = 1\n", encoding="utf-8")

    result = analyze_python_source(source_file, project_root=tmp_path)

    assert result.docstring is None
    assert result.imports == []
    assert result.classes == []
    assert result.functions == []
    assert "module_docstring" in result.missing_fields
    assert "imports" in result.missing_fields
    assert "top_level_symbols" in result.missing_fields


def test_analyze_python_source_ignores_execution_behavior(tmp_path):
    source_file = tmp_path / "exec_guard.py"
    source_file.write_text(
        "import os\n\nVALUE = __import__('os').environ.get('SECRET', 'missing')\n\ndef ready():\n    return VALUE\n",
        encoding="utf-8",
    )

    result = analyze_python_source(source_file, project_root=tmp_path)

    assert result.imports
    assert [fn.name for fn in result.functions] == ["ready"]
    assert result.missing_fields == ["module_docstring"]
