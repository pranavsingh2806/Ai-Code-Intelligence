"""
ast_parser.py
Parses Python source into a lightweight structural summary using the stdlib ast module.
"""
from __future__ import annotations

import ast
from typing import Optional


def parse_python_ast(code: str) -> Optional[dict]:
    """
    Parse *code* and return a dict with three keys:
        classes   – list of top-level class names
        functions – list of module-level function names
        imports   – list of imported module/name strings

    Returns None if the code has a SyntaxError.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    classes:   list[str] = []
    functions: list[str] = []
    imports:   list[str] = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)

        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            functions.append(node.name)

        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.asname or alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                label = f"{module}.{alias.name}" if module else alias.name
                imports.append(alias.asname or label)

    return {"classes": classes, "functions": functions, "imports": imports}


def format_ast_summary(ast_summary: Optional[dict]) -> str:
    """
    Produce a short fenced 'Code structure summary' block suitable for
    injection into an LLM system-prompt, or "" if *ast_summary* is None.
    """
    if not ast_summary:
        return ""

    lines = ["```", "Code structure summary:"]
    if ast_summary.get("classes"):
        lines.append(f"  Classes   : {', '.join(ast_summary['classes'])}")
    if ast_summary.get("functions"):
        lines.append(f"  Functions : {', '.join(ast_summary['functions'])}")
    if ast_summary.get("imports"):
        lines.append(f"  Imports   : {', '.join(ast_summary['imports'])}")
    lines.append("```")
    return "\n".join(lines)
