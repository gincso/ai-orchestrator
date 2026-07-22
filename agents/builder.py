from agents.base import BaseAgent


class BuilderAgent(BaseAgent):
    name = "builder"
    expertise = "infrastructure, Docker, CI/CD, configuration, build tooling"

    def get_system_prompt(self) -> str:
        return (
            "You are a Builder agent. You handle infrastructure, configuration, "
            "Dockerfiles, CI/CD pipelines, and build tooling. "
            "You have access to tools: write_file, read_file, list_files, run_shell. "
            "Create production-ready configurations following best practices."
        )
