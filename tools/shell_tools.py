import subprocess
from tools.registry import register_tool


def run_shell(command: str, timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout[:3000]
        if result.stderr:
            output += f"\n(STDERR): {result.stderr[:1000]}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s"
    except Exception as e:
        return f"Shell error: {e}"


register_tool(
    name="run_shell",
    description="Run a shell command in the container",
    fn=run_shell,
    parameters={
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Shell command to execute"},
            "timeout": {"type": "integer", "description": "Timeout in seconds"},
        },
        "required": ["command"],
    },
)
