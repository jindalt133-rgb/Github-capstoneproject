from pathlib import Path

from doc_sync.cli import main


def test_cli_reports_no_drift_and_exits_zero(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('demo')\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname = \"demo-app\"\n", encoding="utf-8")
    manifest = repo / "docs" / "technical-app-manifest.md"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        """# Technical App Manifest

## Overview
- Application Name: demo-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python
- Deployment Pipeline: Not Found
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: Not Found
- Last Updated: 2025-01-01T00:00:00Z
""",
        encoding="utf-8",
    )

    exit_code = main([str(repo)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "No drift detected" in captured.out


def test_cli_reports_update_and_returns_zero(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "demo.py").write_text("print('demo')\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname = \"demo-app\"\n", encoding="utf-8")
    manifest = repo / "docs" / "technical-app-manifest.md"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        """# Technical App Manifest

## Overview
- Application Name: old-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: https://github.com/example/demo.git
- Last Updated: 2025-01-01T00:00:00Z
""",
        encoding="utf-8",
    )

    exit_code = main([str(repo)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Synchronization complete" in captured.out
    assert "Application Name" in captured.out


def test_cli_returns_non_zero_when_synchronization_fails(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project\nname = \"broken\"\npassword = \"super-secret\"\n", encoding="utf-8")
    manifest = repo / "docs" / "technical-app-manifest.md"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        """# Technical App Manifest

## Overview
- Application Name: old-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: Example summary.
- Language/Runtime: Python
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: Not Found
- Last Updated: 2025-01-01T00:00:00Z
""",
        encoding="utf-8",
    )

    exit_code = main([str(repo)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Synchronization failed" in captured.err
    assert "Malformed authoritative configuration file: pyproject.toml" in captured.err
    assert "super-secret" not in captured.err
