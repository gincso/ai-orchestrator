import json
from typing import Optional
from config import settings
from core.event_bus import publish
from core.task import TaskStatus
from tools.registry import get_openai_tools, dispatch
from utils.llm import call_llm_with_tools, call_llm
from utils.helpers import logger


class BaseAgent:
    name: str = "base"
    expertise: str = "general"

    def __init__(self, project_id: int):
        self.project_id = project_id

    def _emit(self, event_type: str, data: dict):
        publish(str(self.project_id), event_type, {**data, "agent": self.name})

    def get_system_prompt(self) -> str:
        return f"You are {self.name}, an AI agent with expertise in {self.expertise}."

    def run(self, task_description: str, context: Optional[str] = None) -> str:
        self._emit("agent_status", {"status": "started", "task": task_description})

        system = self.get_system_prompt()
        if context:
            collaborator_info = (
                "\n\n## Results from peer agents you depend on\n"
                "Other agents have already completed work that you should build upon. "
                "Read their outputs carefully and incorporate their findings into your work. "
                "Do not duplicate work already done.\n"
                + context
            )
            system += collaborator_info

        tools = get_openai_tools()
        messages = [{"role": "system", "content": system}]
        messages.append({"role": "user", "content": task_description})
        turn_count = 0

        while turn_count < 15:
            resp = call_llm_with_tools(system, "", tools, messages=messages)
            tool_calls = getattr(resp, "tool_calls", None)

            if not tool_calls:
                final = resp.content or ""
                self._emit("agent_status", {"status": "completed", "result": final[:200]})
                return final

            for tc in tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                self._emit("agent_status", {"status": "tool_call", "tool": name, "args": args})
                result = dispatch(name, **args)
                messages.append({"role": "assistant", "tool_calls": [tc]})
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})

            turn_count += 1

        self._emit("agent_status", {"status": "max_turns"})
        return "Reached maximum turns without completion."

    def run_simple(self, system_prompt: str, user_prompt: str, model: str = "") -> str:
        self._emit("agent_status", {"status": "thinking"})
        result = call_llm(system_prompt, user_prompt, model=model)
        self._emit("agent_status", {"status": "completed", "result": result[:200]})
        return result
