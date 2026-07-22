from typing import Any, Callable

_tools: dict[str, dict] = {}


def register_tool(name: str, description: str, fn: Callable, parameters: dict):
    _tools[name] = {
        "name": name,
        "description": description,
        "fn": fn,
        "parameters": parameters,
    }


def get_tool(name: str) -> dict | None:
    return _tools.get(name)


def get_openai_tools() -> list[dict]:
    result = []
    for t in _tools.values():
        result.append({
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"],
            },
        })
    return result


def dispatch(name: str, **kwargs) -> Any:
    tool = get_tool(name)
    if not tool:
        return {"error": f"Unknown tool: {name}"}
    try:
        return tool["fn"](**kwargs)
    except Exception as e:
        return {"error": str(e)}
