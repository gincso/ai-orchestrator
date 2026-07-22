from pathlib import Path
from tools.registry import register_tool

WORKSPACE_ROOT = Path("./projects")


def read_file(path: str) -> str:
    full = WORKSPACE_ROOT / path
    if not full.exists():
        return f"File not found: {path}"
    return full.read_text()


def write_file(path: str, content: str) -> str:
    full = WORKSPACE_ROOT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content)
    return f"Written: {path} ({len(content)} chars)"


def list_files(path: str = "") -> str:
    target = WORKSPACE_ROOT / path if path else WORKSPACE_ROOT
    if not target.exists():
        return f"Path not found: {path}"
    files = []
    for p in target.rglob("*"):
        if p.is_file():
            files.append(str(p.relative_to(WORKSPACE_ROOT)))
    return "\n".join(files) if files else "(empty)"


register_tool(
    name="read_file",
    description="Read a file from the project workspace",
    fn=read_file,
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative path in workspace"},
        },
        "required": ["path"],
    },
)

register_tool(
    name="write_file",
    description="Write content to a file in the project workspace",
    fn=write_file,
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative path in workspace"},
            "content": {"type": "string", "description": "File content"},
        },
        "required": ["path", "content"],
    },
)

register_tool(
    name="list_files",
    description="List files in the project workspace",
    fn=list_files,
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Subdirectory path"},
        },
    },
)
