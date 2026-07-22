import sys
import io
import traceback
from tools.registry import register_tool


def execute_python(code: str) -> str:
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    try:
        compiled = compile(code, "<exec>", "exec")
        exec(compiled, {"__builtins__": __builtins__})
        out = sys.stdout.getvalue()
        err = sys.stderr.getvalue()
        result = out[:3000]
        if err:
            result += f"\n(STDERR): {err[:1000]}"
        return result or "(no output)"
    except Exception as e:
        return f"Error: {e}\n{traceback.format_exc()[:1000]}"
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


register_tool(
    name="execute_python",
    description="Execute Python code in a sandboxed environment",
    fn=execute_python,
    parameters={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python code to execute"},
        },
        "required": ["code"],
    },
)
