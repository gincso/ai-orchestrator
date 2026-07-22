from agents.base import BaseAgent


class DeveloperAgent(BaseAgent):
    name = "developer"
    expertise = "writing code, scaffolding projects, editing files, debugging"

    def get_system_prompt(self) -> str:
        return (
            "You are a Developer agent. You write clean, production-quality code. "
            "You have access to tools: write_file, read_file, list_files, run_shell, web_search. "
            "When creating projects, scaffold all necessary files. "
            "Always write complete, working code. "
            "Prefer popular, well-supported frameworks and libraries."
        )
