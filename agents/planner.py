import json
from agents.base import BaseAgent
from utils.llm import call_llm


class PlannerAgent(BaseAgent):
    name = "planner"
    expertise = "task decomposition and dependency scheduling"

    def get_system_prompt(self) -> str:
        return (
            "You are a Planner agent. Your job is to break down complex tasks "
            "into smaller sub-tasks and determine their dependencies and execution order. "
            "\n\nRules:\n"
            "- Output ONLY a JSON array of objects.\n"
            "- Each object has keys: title, description, category, depends_on\n"
            "- 'title' is a short name for the sub-task\n"
            "- 'description' is what the agent should do\n"
            "- 'category' is one of: developer, builder, researcher, social_engineer, planner\n"
            "- 'depends_on' is a list of array indices this task depends on (empty list for no deps)\n"
            "- Tasks that can run in parallel should have no dependency on each other\n"
            "- Put research tasks first, then planning, then development, then building\n"
            "- Keep the task list concise — 3 to 6 sub-tasks maximum"
        )

    def decompose(self, task_description: str) -> list[dict]:
        prompt = f"Decompose this task into parallel-friendly sub-tasks:\n\n{task_description}"
        raw = call_llm(self.get_system_prompt(), prompt, temperature=0.2)
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()
            tasks = json.loads(cleaned)
            if isinstance(tasks, list):
                for t in tasks:
                    t.setdefault("depends_on", [])
                    t.setdefault("category", "developer")
                    t.setdefault("description", t.get("title", ""))
                return tasks
        except json.JSONDecodeError:
            pass
        return [{"title": task_description, "description": task_description, "category": "developer", "depends_on": []}]
