from pathlib import Path

from doc_sync.repo_scan import scan_repository_files


def test_recursive_repository_scan_returns_authoritative_files(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "api").mkdir()
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "docs").mkdir()

    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    (tmp_path / "src" / "api" / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (tmp_path / "src" / "api" / "config.toml").write_text("[tool]\n", encoding="utf-8")
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: CI\n", encoding="utf-8")
    (tmp_path / "tests" / "test_main.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")

    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "docs" / "guide.md").write_text("Guide\n", encoding="utf-8")
    (tmp_path / "docs" / "technical-app-manifest.md").write_text("Manifest\n", encoding="utf-8")

    result = scan_repository_files(tmp_path)

    assert result == [
        ".github/workflows/ci.yml",
        "pyproject.toml",
        "src/api/config.toml",
        "src/api/main.py",
        "tests/test_main.py",
    ]


def test_recursive_scan_excludes_readme_and_documentation_files(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "notes").mkdir()

    (tmp_path / "README.md").write_text("README\n", encoding="utf-8")
    (tmp_path / "docs" / "overview.md").write_text("overview\n", encoding="utf-8")
    (tmp_path / "notes" / "reference.txt").write_text("text\n", encoding="utf-8")

    assert scan_repository_files(tmp_path) == []


def test_scan_excludes_manifest_and_handles_nested_directories(tmp_path):
    (tmp_path / "nested" / "config").mkdir(parents=True)
    (tmp_path / "docs").mkdir()

    (tmp_path / "nested" / "config" / "settings.yaml").write_text("db: sqlite\n", encoding="utf-8")
    (tmp_path / "docs" / "technical-app-manifest.md").write_text("manifest\n", encoding="utf-8")

    assert scan_repository_files(tmp_path) == ["nested/config/settings.yaml"]


def test_scan_returns_sorted_results_for_deterministic_behavior(tmp_path):
    (tmp_path / "zeta").mkdir()
    (tmp_path / "alpha").mkdir()

    (tmp_path / "zeta" / "b.py").write_text("print('b')\n", encoding="utf-8")
    (tmp_path / "alpha" / "a.py").write_text("print('a')\n", encoding="utf-8")

    assert scan_repository_files(tmp_path) == ["alpha/a.py", "zeta/b.py"]


def test_empty_or_no_source_repository_is_handled_safely(tmp_path):
    assert scan_repository_files(tmp_path) == []

    (tmp_path / "docs").mkdir()
    (tmp_path / "notes.md").write_text("notes\n", encoding="utf-8")
    assert scan_repository_files(tmp_path) == []
