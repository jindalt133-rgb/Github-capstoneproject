from __future__ import annotations

from pathlib import Path

from automated_documentation_sync.analysis import (
    FileProcessingError,
    analyze_python_files,
    format_processing_errors,
)


def test_invalid_python_file_does_not_prevent_valid_file_processing(tmp_path):
    valid_file = tmp_path / "valid.py"
    valid_file.write_text(
        '"""Valid module."""\n\n\ndef run():\n    return "ok"\n',
        encoding="utf-8",
    )
    invalid_file = tmp_path / "invalid.py"
    invalid_file.write_text("def broken(:\n", encoding="utf-8")

    report = analyze_python_files([invalid_file, valid_file], project_root=tmp_path)

    assert [module.module_name for module in report.modules] == ["valid"]
    assert len(report.errors) == 1
    assert report.errors[0].path == "invalid.py"
    assert report.errors[0].error_type == "SyntaxError"
    assert "invalid.py" in format_processing_errors(report.errors)


def test_missing_or_unreadable_input_is_reported_gracefully(tmp_path):
    valid_file = tmp_path / "good.py"
    valid_file.write_text('"""Good module."""\n', encoding="utf-8")
    missing_file = tmp_path / "missing.py"

    report = analyze_python_files([missing_file, valid_file], project_root=tmp_path)

    assert [module.module_name for module in report.modules] == ["good"]
    assert len(report.errors) == 1
    assert report.errors[0].path == "missing.py"
    assert report.errors[0].error_type == "FileNotFoundError"
    assert "missing.py" in format_processing_errors(report.errors)


def test_processing_errors_are_deterministic_and_clear(tmp_path):
    valid_file = tmp_path / "good.py"
    valid_file.write_text('"""Good module."""\n', encoding="utf-8")
    broken_file = tmp_path / "broken.py"
    broken_file.write_text("if True:\n", encoding="utf-8")

    report = analyze_python_files([broken_file, valid_file], project_root=tmp_path)

    rendered = format_processing_errors(report.errors)
    assert rendered == "Processing errors:\n- broken.py: SyntaxError: invalid Python source"


def test_successful_results_are_preserved_alongside_failures(tmp_path):
    good_file = tmp_path / "alpha.py"
    good_file.write_text('"""Alpha module."""\n\n\ndef value():\n    return 1\n', encoding="utf-8")
    bad_file = tmp_path / "beta.py"
    bad_file.write_text("x = [\n", encoding="utf-8")

    report = analyze_python_files([bad_file, good_file], project_root=tmp_path)

    assert len(report.modules) == 1
    assert report.modules[0].module_name == "alpha"
    assert len(report.errors) == 1
    assert report.errors[0].path == "beta.py"


def test_error_reporting_uses_stable_sorting(tmp_path):
    errors = [
        FileProcessingError(path="zeta.py", error_type="SyntaxError", message="bad"),
        FileProcessingError(path="alpha.py", error_type="FileNotFoundError", message="missing"),
    ]

    rendered = format_processing_errors(errors)

    assert rendered.index("alpha.py") < rendered.index("zeta.py")
    assert rendered.startswith("Processing errors:\n- alpha.py: FileNotFoundError: missing")
