from agents.base import BaseAgent
from agents.developer import DeveloperAgent
from agents.builder import BuilderAgent
from agents.researcher import ResearcherAgent
from agents.social_engineer import SocialEngineerAgent
from agents.planner import PlannerAgent
from core.event_bus import publish
from utils.helpers import logger


AGENT_MAP = {
    "developer": DeveloperAgent,
    "builder": BuilderAgent,
    "researcher": ResearcherAgent,
    "social_engineer": SocialEngineerAgent,
    "planner": PlannerAgent,
}


def create_agent(agent_type: str, project_id: int) -> BaseAgent:
    cls = AGENT_MAP.get(agent_type)
    if not cls:
        logger.warning(f"Unknown agent type '{agent_type}', falling back to developer")
        cls = DeveloperAgent
    return cls(project_id)


def run_subtask(project_id: int, task_id: int, agent_type: str, title: str, description: str) -> str:
    publish(str(project_id), "task_status", {
        "task_id": task_id, "status": "running", "agent": agent_type, "title": title
    })
    agent = create_agent(agent_type, project_id)
    result = agent.run(description)
    publish(str(project_id), "task_status", {
        "task_id": task_id, "status": "done", "agent": agent_type, "title": title
    })
    return result
