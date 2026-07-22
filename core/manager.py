import json
from datetime import datetime, timezone
from typing import Optional

from config import settings
from core.event_bus import publish
from core.task import TaskStatus
from agents.planner import PlannerAgent
from agents.subagent import run_subtask, create_agent
from storage.db import get_session
from storage.models import Project, Task, AgentRun, Artifact, ProjectStatus, TaskStatus as DBTaskStatus
from utils.helpers import logger, write_file
from utils.llm import call_llm


class OrchestratorManager:
    def __init__(self, project_id: int):
        self.project_id = project_id
        self.planner = PlannerAgent(project_id)

    def _emit(self, event_type: str, data: dict):
        publish(str(self.project_id), event_type, {"agent": "manager", **data})

    def create_project(self, name: str, description: str = "") -> Project:
        session = get_session()
        proj = Project(name=name, description=description)
        session.add(proj)
        session.commit()
        session.refresh(proj)
        session.close()
        self._emit("project_created", {"id": proj.id, "name": name})
        return proj

    def submit_task(self, description: str, title: str = "") -> Task:
        self._emit("manager_status", {"status": "analyzing", "task": description})

        session = get_session()
        db_task = Task(
            project_id=self.project_id,
            title=title or description[:80],
            description=description,
            category="general",
            assigned_agent="manager",
            status=DBTaskStatus.IN_PROGRESS,
        )
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        task_id = db_task.id

        self._emit("task_created", {"task_id": task_id, "title": db_task.title})

        self._emit("manager_status", {"status": "decomposing", "task": description})
        sub_tasks = self.planner.decompose(description)
        self._emit("manager_status", {
            "status": "decomposed",
            "sub_tasks": len(sub_tasks),
            "details": [s.get("title", "") for s in sub_tasks],
        })

        results = []
        completed = []
        for i, st in enumerate(sub_tasks):
            agent_type = st.get("category", "developer")
            depends = st.get("depends_on", [])

            deps_met = all(d < len(completed) for d in depends)

            child = Task(
                project_id=self.project_id,
                parent_task_id=task_id,
                title=st.get("title", f"Sub-task {i+1}"),
                description=st.get("description", ""),
                category=agent_type,
                assigned_agent=agent_type,
                status=DBTaskStatus.PENDING if not deps_met else DBTaskStatus.IN_PROGRESS,
            )
            session.add(child)
            session.commit()
            session.refresh(child)

            self._emit("subtask_created", {
                "sub_task_id": child.id,
                "agent": agent_type,
                "title": child.title,
                "depends_on": depends,
            })

            result = run_subtask(
                self.project_id, child.id, agent_type, child.title,
                child.description or child.title,
            )
            results.append(result)
            completed.append(i)

            child.status = DBTaskStatus.COMPLETED
            child.result = result[:2000] if result else ""
            session.add(child)

            run_log = AgentRun(
                task_id=child.id,
                agent_name=agent_type,
                input_data=child.description or child.title,
                output_data=result[:2000] if result else "",
                ended_at=datetime.now(timezone.utc),
            )
            session.add(run_log)

            project_dir = f"projects/project_{self.project_id}"
            file_path = f"{project_dir}/{agent_type}_{child.id}.md"
            write_file(file_path, f"# {child.title}\n\n{result}\n")
            session.add(Artifact(
                task_id=child.id,
                file_path=file_path,
                artifact_type="markdown",
                description=child.title,
            ))

            session.commit()
            self._emit("artifact_created", {
                "task_id": child.id, "path": file_path, "agent": agent_type
            })

        db_task.status = DBTaskStatus.COMPLETED
        db_task.result = "\n\n".join(results)[:3000]
        session.add(db_task)
        session.commit()
        session.close()

        self._emit("manager_status", {"status": "completed", "total_subtasks": len(sub_tasks)})
        self._learn_and_create_skill(description, results)

        return db_task

    def _learn_and_create_skill(self, description: str, results: list[str]):
        prompt = (
            "Based on the following task and results, create a reusable skill document "
            "in markdown format. Include: skill name, description, when to use it, "
            "steps, and warnings.\n\n"
            f"Task: {description}\n\nResults:\n" + "\n".join(r[:500] for r in results)
        )
        system = "You are a skill curator. Write concise, reusable skill documents."
        skill_content = call_llm(system, prompt, temperature=0.3)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        safe_name = description.replace(" ", "_").replace("/", "_")[:40]
        path = f"skills/{timestamp}_{safe_name}.md"
        write_file(path, skill_content)
        self._emit("skill_created", {"path": path})
