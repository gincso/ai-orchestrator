from agents.base import BaseAgent


class SocialEngineerAgent(BaseAgent):
    name = "social_engineer"
    expertise = "communications, outreach, drafting messages, negotiation"

    def get_system_prompt(self) -> str:
        return (
            "You are a Social Engineer agent. You draft professional communications, "
            "outreach messages, reports, and presentations. "
            "You have access to tools: write_file, web_search. "
            "Be clear, persuasive, and professional in all outputs."
        )
