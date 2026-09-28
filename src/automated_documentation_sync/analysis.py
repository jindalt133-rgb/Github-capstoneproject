from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FunctionInfo:
    name: str
    lineno: int
    returns: str | None = None


@dataclass
class ClassInfo:
    name: str
    lineno: int
    bases: list[str] = field(default_factory=list)
    methods: list[FunctionInfo] = field(default_factory=list)


@dataclass
class ModuleInfo:
    path: str
    module_name: str
    docstring: str | None = None
    imports: list[str] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)


def _safe_relpath(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _extract_function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionInfo:
    returns = None
    for child in ast.walk(node):
        if isinstance(child, ast.AnnAssign):
            if child.target.id == "return":
                returns = ast.unparse(child.value)
        if isinstance(child, ast.Return):
            if child.value is not None:
                returns = ast.unparse(child.value)
    return FunctionInfo(name=node.name, lineno=getattr(node, "lineno", 0), returns=returns)


def analyze_python_source(file_path: str | Path, project_root: str | Path | None = None) -> ModuleInfo:
    """Parse a Python file and extract only documentation-relevant metadata without executing it."""
    source_path = Path(file_path)
    root = Path(project_root) if project_root is not None else source_path.parent
    source_text = source_path.read_text(encoding="utf-8")
    module_ast = ast.parse(source_text, filename=str(source_path))

    module_name = source_path.stem
    imports: list[str] = []
    classes: list[ClassInfo] = []
    functions: list[FunctionInfo] = []
    missing_fields: list[str] = []

    for node in module_ast.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(ast.unparse(node))
        elif isinstance(node, (ast.ClassDef, ast.AsyncFunctionDef)):
            if isinstance(node, ast.ClassDef):
                bases = [ast.unparse(base) for base in node.bases]
                class_methods: list[FunctionInfo] = []
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        class_methods.append(_extract_function_signature(child))
                classes.append(ClassInfo(name=node.name, lineno=getattr(node, "lineno", 0), bases=bases, methods=class_methods))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(_extract_function_signature(node))

    if not imports:
        missing_fields.append("imports")
    if not classes and not functions:
        missing_fields.append("top_level_symbols")

    docstring = ast.get_docstring(module_ast)
    if docstring is None:
        missing_fields.append("module_docstring")

    return ModuleInfo(
        path=_safe_relpath(source_path, root),
        module_name=module_name,
        docstring=docstring,
        imports=imports,
        classes=classes,
        functions=functions,
        missing_fields=missing_fields,
    )
