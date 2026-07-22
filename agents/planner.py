import json
from agents.base import BaseAgent
from utils.llm import call_llm


class PlannerAgent(BaseAgent):
    name = "planner"
    expertise = "task decomposition and dependency scheduling"

    def get_system_prompt(self) -> str:
        return (
            "You are a Planner agent. Your job is to break down complex tasks "
            "into smaller sub-tasks and determine their dependencies and order. "
            "Output a JSON array of objects with keys: title, description, category, depends_on (list of indices). "
            "Categories: developer, builder, researcher, social_engineer, planner."
        )

    def decompose(self, task_description: str) -> list[dict]:
        prompt = f"Decompose this task into sub-tasks:\n\n{task_description}"
        raw = call_llm(self.get_system_prompt(), prompt, temperature=0.2)
        try:
            cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
            tasks = json.loads(cleaned)
            if isinstance(tasks, list):
                return tasks
        except json.JSONDecodeError:
            pass
        return [{"title": task_description, "description": task_description, "category": "developer", "depends_on": []}]
