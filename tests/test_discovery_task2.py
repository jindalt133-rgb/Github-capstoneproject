from __future__ import annotations

from pathlib import Path

from automated_documentation_sync.discovery import DEFAULT_EXCLUDED_DIR_NAMES, discover_python_files


def test_discover_python_files_ignores_default_exclusions(tmp_path):
    project_root = tmp_path / "project"
    (project_root / "pkg").mkdir(parents=True)
    (project_root / "pkg" / "alpha.py").write_text("print('alpha')\n", encoding="utf-8")
    (project_root / "pkg" / "beta.py").write_text("print('beta')\n", encoding="utf-8")
    (project_root / ".git").mkdir()
    (project_root / ".git" / "ignored.py").write_text("print('ignored')\n", encoding="utf-8")
    (project_root / "tests").mkdir()
    (project_root / "tests" / "ignored_test.py").write_text("print('test')\n", encoding="utf-8")
    (project_root / "build").mkdir()
    (project_root / "build" / "artifact.py").write_text("print('build')\n", encoding="utf-8")
    (project_root / "docs").mkdir()
    (project_root / "docs" / "generated").mkdir()
    (project_root / "docs" / "generated" / "source-documentation.md").write_text("# docs\n", encoding="utf-8")

    discovered = discover_python_files(project_root)

    assert {path.relative_to(project_root).as_posix() for path in discovered} == {
        "pkg/alpha.py",
        "pkg/beta.py",
    }
    assert {".git", "tests", "build", "generated"}.issubset(DEFAULT_EXCLUDED_DIR_NAMES)


def test_discover_python_files_rejects_missing_root(tmp_path):
    missing_root = tmp_path / "missing"

    try:
        discover_python_files(missing_root)
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_discover_python_files_rejects_file_root(tmp_path):
    file_root = tmp_path / "not_a_dir.txt"
    file_root.write_text("hello", encoding="utf-8")

    try:
        discover_python_files(file_root)
        assert False, "Expected NotADirectoryError"
    except NotADirectoryError:
        pass
