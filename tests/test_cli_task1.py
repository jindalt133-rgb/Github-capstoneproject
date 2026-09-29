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


def test_cli_generates_documentation_from_valid_python_project(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()
    source_dir = project_root / "pkg"
    source_dir.mkdir()
    (source_dir / "services.py").write_text(
        '''"""Service module."""\n\nAPI_KEY = "abc123"\n\nclass Worker:\n    """Worker class."""\n\n    def run(self, value: str) -> str:\n        return value\n\n\ndef build_service() -> str:\n    return "ready"\n''',
        encoding="utf-8",
    )

    exit_code = main(["--project-root", str(project_root)])
    output_path = project_root / "docs" / "generated" / "source-documentation.md"

    assert exit_code == 0
    assert output_path.exists()
    output_text = output_path.read_text(encoding="utf-8")
    assert "Repository Documentation" in output_text
    assert "Worker" in output_text
    assert "build_service" in output_text
    assert "abc123" not in output_text


def test_cli_handles_invalid_file_without_blocking_valid_output(tmp_path, capsys):
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "valid.py").write_text(
        '"""Valid module."""\n\n\ndef run():\n    return "ok"\n',
        encoding="utf-8",
    )
    (project_root / "broken.py").write_text("def broken(:\n", encoding="utf-8")

    exit_code = main(["--project-root", str(project_root)])
    output_path = project_root / "docs" / "generated" / "source-documentation.md"
    captured = capsys.readouterr()

    assert exit_code == 0
    assert output_path.exists()
    assert "valid" in output_path.read_text(encoding="utf-8").lower()
    assert "Processing errors:" in captured.out
    assert "broken.py" in captured.out


def test_cli_reuses_existing_documentation_on_noop_and_updates_on_meaningful_change(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()
    source_file = project_root / "service.py"
    source_file.write_text(
        '"""Current module."""\n\n\ndef run() -> str:\n    return "ready"\n',
        encoding="utf-8",
    )

    first_exit = main(["--project-root", str(project_root)])
    first_content = (project_root / "docs" / "generated" / "source-documentation.md").read_text(encoding="utf-8")

    second_exit = main(["--project-root", str(project_root)])
    second_content = (project_root / "docs" / "generated" / "source-documentation.md").read_text(encoding="utf-8")

    assert first_exit == 0
    assert second_exit == 0
    assert first_content == second_content

    source_file.write_text(
        '"""Current module."""\n\n\ndef run() -> int:\n    return 42\n',
        encoding="utf-8",
    )

    third_exit = main(["--project-root", str(project_root)])
    third_content = (project_root / "docs" / "generated" / "source-documentation.md").read_text(encoding="utf-8")

    assert third_exit == 0
    assert third_content != second_content
    assert "int" in third_content
