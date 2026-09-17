from pathlib import Path

from doc_sync.extractors import extract_repository_metadata


def test_extract_python_runtime_and_version_from_authoritative_sources(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "demo").mkdir()
    (tmp_path / "src" / "demo" / "app.py").write_text("print('demo')\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = \"demo-app\"\nversion = \"0.2.0\"\nrequires-python = \">=3.11\"\n",
        encoding="utf-8",
    )

    metadata = extract_repository_metadata(tmp_path)

    assert metadata["Language/Runtime"] == "Python"
    assert metadata["Current Version"] == "0.2.0"
    assert metadata["Application Name"] == "demo-app"


def test_extract_frameworks_and_dependencies_from_project_config(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        "[project]\ndependencies = ['fastapi', 'uvicorn', 'pytest']\n",
        encoding="utf-8",
    )

    metadata = extract_repository_metadata(tmp_path)

    assert "FastAPI" in metadata["Frameworks"]
    assert "fastapi" in metadata["Upstream Dependencies"]


def test_extract_test_and_pipeline_metadata(tmp_path):
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text(
        "name: CI\n on: [push]\n jobs:\n   test:\n     runs-on: ubuntu-latest\n",
        encoding="utf-8",
    )
    (tmp_path / "pytest.ini").write_text("[pytest]\naddopts = --cov\n", encoding="utf-8")

    metadata = extract_repository_metadata(tmp_path)

    assert metadata["Test Frameworks"] == "pytest"
    assert metadata["Deployment Pipeline"] == "GitHub Actions"
    assert metadata["Code Coverage Goal"] == "--cov"


def test_extract_database_and_repository_when_present(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "settings.py").write_text("DATABASE_URL = 'sqlite:///app.db'\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("[remote \"origin\"]\n    url = https://github.com/example/demo.git\n", encoding="utf-8")

    metadata = extract_repository_metadata(tmp_path)

    assert metadata["Primary Database"] == "SQLite"
    assert metadata["GitHub Repository"] == "https://github.com/example/demo.git"


def test_missing_metadata_returns_not_found(tmp_path):
    metadata = extract_repository_metadata(tmp_path)

    for field in [
        "Application Name",
        "Language/Runtime",
        "Frameworks",
        "Primary Database",
        "Cloud Provider",
        "Infrastructure",
        "Upstream Dependencies",
        "Main Branch",
        "Build Tool",
        "Critical Env Variables",
        "Deployment Pipeline",
        "Test Frameworks",
        "Code Coverage Goal",
        "Security Scanning",
        "Observation/Logging",
        "GitHub Repository",
        "API Documentation",
        "Current Version",
    ]:
        assert metadata[field] == "Not Found"


def test_readme_content_is_not_used_as_authoritative_source(tmp_path):
    (tmp_path / "README.md").write_text("# Demo app\nFastAPI\n",
                                       encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "notes.md").write_text("This project uses FastAPI\n", encoding="utf-8")

    metadata = extract_repository_metadata(tmp_path)

    assert metadata["Frameworks"] == "Not Found"
    assert metadata["Language/Runtime"] == "Not Found"


def test_multiple_source_files_are_handled_deterministically(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "alpha.py").write_text("print('alpha')\n", encoding="utf-8")
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "settings.yaml").write_text("db: sqlite\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'alpha-app'\n", encoding="utf-8")

    metadata = extract_repository_metadata(tmp_path)

    assert metadata["Application Name"] == "alpha-app"
    assert metadata["Primary Database"] == "SQLite"
    assert metadata["Language/Runtime"] == "Python"
