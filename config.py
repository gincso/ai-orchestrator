from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    openrouter_api_key: str = ""
    orchestrator_model: str = "deepseek/deepseek-v4-flash:free"
    agent_model: str = "deepseek/deepseek-v4-flash:free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    database_url: str = "sqlite:///./data/orchestrator.db"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
