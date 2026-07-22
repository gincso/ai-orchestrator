from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(str, Enum):
    PLANNER = "planner"
    DEVELOPER = "developer"
    BUILDER = "builder"
    RESEARCHER = "researcher"
    SOCIAL_ENGINEER = "social_engineer"
    MANAGER = "manager"
    SUBAGENT = "subagent"


@dataclass
class Task:
    title: str
    description: str = ""
    category: str = "general"
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: str = ""
    priority: int = 0
    parent_task_id: Optional[int] = None
    result: Optional[str] = None
    error: Optional[str] = None
    id: Optional[int] = None
    project_id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
