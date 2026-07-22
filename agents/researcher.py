from agents.base import BaseAgent


class ResearcherAgent(BaseAgent):
    name = "researcher"
    expertise = "web research, information gathering, analysis, summarization"

    def get_system_prompt(self) -> str:
        return (
            "You are a Researcher agent. You gather information from the web, "
            "analyze documents, and produce concise summaries. "
            "You have access to tools: web_search, fetch_url. "
            "Cite your sources and prioritize reliable information."
        )
