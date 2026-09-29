from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analysis import analyze_python_files, format_processing_errors
from .discovery import discover_python_files
from .filtering import filter_sensitive_metadata
from .generation import write_generated_documentation

DEFAULT_OUTPUT_PATH = Path("docs/generated/source-documentation.md")


def resolve_project_root(project_root: str | None) -> Path:
    """Resolve the project root and validate it is a directory."""
    root = Path(project_root).expanduser() if project_root is not None else Path.cwd()
    if not root.exists():
        raise FileNotFoundError(f"Project root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Project root is not a directory: {root}")
    return root.resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Synchronize generated repository documentation from Python source files."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Path to the repository root to analyze.",
    )
    return parser


def _build_documentation_metadata(project_root: Path) -> dict[str, object]:
    discovered_files = discover_python_files(project_root)
    report = analyze_python_files(discovered_files, project_root=project_root)

    modules: list[dict[str, object]] = []
    for module in report.modules:
        modules.append(
            {
                "module_name": module.module_name,
                "path": module.path,
                "docstring": module.docstring,
                "imports": module.imports,
                "classes": [
                    {
                        "name": class_info.name,
                        "lineno": class_info.lineno,
                        "bases": class_info.bases,
                        "methods": [
                            {
                                "name": method.name,
                                "lineno": method.lineno,
                                "returns": method.returns,
                            }
                            for method in class_info.methods
                        ],
                    }
                    for class_info in module.classes
                ],
                "functions": [
                    {
                        "name": function.name,
                        "lineno": function.lineno,
                        "returns": function.returns,
                    }
                    for function in module.functions
                ],
                "missing_fields": module.missing_fields,
            }
        )

    metadata = {"modules": modules}
    return filter_sensitive_metadata(metadata)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        project_root = resolve_project_root(args.project_root)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    output_path = project_root / DEFAULT_OUTPUT_PATH
    relative_output_path = output_path.relative_to(project_root)
    print(f"Project root: {project_root}")
    print(f"Output path: {str(relative_output_path).replace('\\', '/')}" )

    try:
        report = analyze_python_files(discover_python_files(project_root), project_root=project_root)
        if report.errors:
            print(format_processing_errors(report.errors))
        metadata = _build_documentation_metadata(project_root)
        write_generated_documentation(project_root, metadata)
        if output_path.exists():
            print(f"Documentation generated: {str(relative_output_path).replace('\\', '/')}" )
        return 0
    except Exception as exc:  # pragma: no cover - unexpected runtime failure
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
