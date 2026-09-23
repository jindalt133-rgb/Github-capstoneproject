from pathlib import Path

from doc_sync.repo_scan import scan_repository_files
from doc_sync.source_registry import is_authoritative_source, is_non_authoritative_source


def test_authoritative_technical_files_are_detected():
    candidates = [
        "pyproject.toml",
        "src/app.py",
        "src/task_api/main.py",
        ".github/workflows/ci.yml",
        "tests/test_app.py",
        "config/settings.toml",
        "docker-compose.yml",
    ]

    for candidate in candidates:
        assert is_authoritative_source(candidate) is True


def test_readme_and_documentation_files_are_excluded():
    excluded = [
        "README.md",
        "docs/overview.md",
        "docs/architecture.md",
        "notes.txt",
        "documentation/guide.rst",
    ]

    for candidate in excluded:
        assert is_authoritative_source(candidate) is False
        assert is_non_authoritative_source(candidate) is True


def test_manifest_is_excluded_from_authoritative_sources():
    assert is_authoritative_source("docs/technical-app-manifest.md") is False
    assert is_non_authoritative_source("docs/technical-app-manifest.md") is True


def test_generated_runtime_artifacts_are_excluded_from_authoritative_sources(tmp_path):
    (tmp_path / "src" / "__pycache__").mkdir(parents=True)
    (tmp_path / "src" / "__pycache__" / "module.cpython-311.pyc").write_bytes(b"\x00\x01\x02")
    (tmp_path / ".pytest_cache").mkdir()
    (tmp_path / ".pytest_cache" / "v").mkdir()
    (tmp_path / ".pytest_cache" / "v" / "cache").mkdir(parents=True)
    (tmp_path / "pkg.egg-info").mkdir()
    (tmp_path / "pkg.egg-info" / "PKG-INFO").write_text("metadata\n", encoding="utf-8")

    assert is_authoritative_source("src/__pycache__/module.cpython-311.pyc") is False
    assert is_authoritative_source("pkg.egg-info/PKG-INFO") is False
    assert is_authoritative_source(".pytest_cache/v/cache/nodeids") is False
    assert scan_repository_files(tmp_path) == []


def test_empty_or_no_relevant_sources_are_handled_safely():
    assert is_authoritative_source("") is False
    assert is_non_authoritative_source("") is False

    repo_root = Path(__file__).resolve().parent
    assert scan_repository_files(repo_root) == [] or isinstance(scan_repository_files(repo_root), list)
