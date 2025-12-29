"""Script execution with parameter injection and result capture."""

import ast
import traceback
from pathlib import Path
from typing import Any

from PIL import Image


def execute_script(
    script_path: Path | str, parameters: dict[str, Any]
) -> Image.Image:
    """Execute a script file with parameters injected as globals.

    The script is executed using exec() with full system access. Only run
    scripts you trust - they can read/write files, make network requests,
    and execute arbitrary code.

    Args:
        script_path: Path to the Python script to execute.
        parameters: Dictionary of parameter values to inject as globals.

    Returns:
        The PIL Image produced by the script's final expression.

    Raises:
        ValueError: If the script doesn't exist, doesn't produce a PIL Image,
            or execution fails.
    """
    script_path = Path(script_path)

    try:
        script_content = script_path.read_text()
    except FileNotFoundError:
        raise ValueError(f"Script not found: {script_path}") from None

    try:
        tree = ast.parse(script_content, filename=str(script_path))
    except SyntaxError as e:
        raise ValueError(f"Syntax error in script: {e}") from e

    result_var = "_result_"
    has_final_expression = tree.body and isinstance(tree.body[-1], ast.Expr)

    if has_final_expression:
        last_expr = tree.body[-1]
        assignment = ast.Assign(
            targets=[ast.Name(id=result_var, ctx=ast.Store())],
            value=last_expr.value,
        )
        ast.copy_location(assignment, last_expr)
        tree.body[-1] = assignment
        ast.fix_missing_locations(tree)

    compiled = compile(tree, filename=str(script_path), mode="exec")

    exec_globals = dict(parameters)

    try:
        exec(compiled, exec_globals)
    except Exception as e:
        tb = traceback.format_exc()
        raise ValueError(f"Script execution failed:\n{tb}") from e

    result = exec_globals.get(result_var)

    if not isinstance(result, Image.Image):
        if not has_final_expression:
            raise ValueError(
                "Script must end with an expression that evaluates to a PIL Image. "
                "Add the image variable as a bare expression on the last line "
                "(e.g., 'img' not 'img = ...')."
            )
        result_type = type(result).__name__ if result is not None else "None"
        raise ValueError(
            f"Script must return a PIL Image, got {result_type}. "
            "Ensure the last expression evaluates to a PIL Image."
        )

    return result
