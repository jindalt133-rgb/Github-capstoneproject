from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from automated_documentation_sync.cli import main


def test_cli_accepts_valid_project_root(tmp_path, capsys):
    project_root = tmp_path / "project"
    project_root.mkdir()

    exit_code = main(["--project-root", str(project_root)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert f"Project root: {project_root.resolve()}" in captured.out
    assert "docs/generated/source-documentation.md" in captured.out


def test_cli_rejects_missing_project_root(capsys):
    missing_path = Path("/definitely/does/not/exist")

    exit_code = main(["--project-root", str(missing_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Project root does not exist" in captured.err


def test_module_entrypoint_runs_with_python_m(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()

    result = subprocess.run(
        [sys.executable, "-m", "automated_documentation_sync", "--project-root", str(project_root)],
        cwd=str(Path(__file__).resolve().parents[1]),
        env={**dict(__import__("os").environ), "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Project root:" in result.stdout
    assert "docs/generated/source-documentation.md" in result.stdout
