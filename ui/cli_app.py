import typer
from typing import Optional
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box

from storage.db import init_db, get_session
from storage.models import Project, Task, ProjectStatus
from core.event_bus import subscribe
from core.manager import OrchestratorManager

cli = typer.Typer()
console = Console()

_status_data: dict = {
    "manager": [],
    "agents": {},
    "tasks": [],
    "artifacts": [],
    "project_name": "",
}


def _build_table() -> Table:
    table = Table(title="AI Orchestrator — Live Status", box=box.ROUNDED)
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Detail")

    for entry in _status_data["manager"][-5:]:
        table.add_row("Manager", "●", entry)

    for agent_name, entries in _status_data["agents"].items():
        last = entries[-1] if entries else ""
        table.add_row(agent_name, "●", last[:60])

    if _status_data["artifacts"]:
        table.add_row("", "", "")
        for a in _status_data["artifacts"][-3:]:
            table.add_row("📄 Artifact", "✓", a[:60])

    return table


def _event_handler(payload):
    ev = payload.get("event", "")
    data = payload.get("data", {})
    agent = data.get("agent", "")

    if ev == "manager_status":
        s = data.get("status", "")
        if s == "decomposed":
            details = data.get("details", [])
            _status_data["manager"].append(f"Decomposed into {data.get('sub_tasks', 0)} sub-tasks")
            for d in details:
                _status_data["manager"].append(f"  → {d}")
        else:
            _status_data["manager"].append(data.get("task", s))
    elif ev == "agent_status":
        aname = data.get("agent", agent)
        if aname:
            _status_data["agents"].setdefault(aname, [])
            s = data.get("status", "")
            if s == "tool_call":
                _status_data["agents"][aname].append(f"Using tool: {data.get('tool', '')}")
            elif s == "completed":
                _status_data["agents"][aname].append("✓ Done")
            elif s == "started":
                _status_data["agents"][aname].append(f"Started: {data.get('task', '')[:50]}")
            else:
                _status_data["agents"][aname].append(s)
    elif ev == "artifact_created":
        _status_data["artifacts"].append(f"{data.get('path', '')}")
    elif ev == "skill_created":
        _status_data["manager"].append(f"📚 Skill saved: {data.get('path', '')}")


@cli.command()
def project_create(name: str, description: str = ""):
    init_db()
    session = get_session()
    proj = Project(name=name, description=description)
    session.add(proj)
    session.commit()
    console.print(f"[green]✓[/] Project '{name}' created (ID: {proj.id})")
    session.close()


@cli.command()
def project_list():
    init_db()
    session = get_session()
    projects = session.query(Project).all()
    if not projects:
        console.print("No projects found.")
        return
    table = Table("ID", "Name", "Status", "Tasks", "Created")
    for p in projects:
        task_count = len(p.tasks)
        table.add_row(str(p.id), p.name, p.status.value, str(task_count), str(p.created_at)[:19])
    console.print(table)
    session.close()


@cli.command()
def task_run(description: str, project_id: int = 0):
    init_db()
    session = get_session()

    if project_id == 0:
        proj = session.query(Project).filter(Project.status == ProjectStatus.ACTIVE).first()
        if not proj:
            proj = Project(name="Default", description="Auto-created project")
            session.add(proj)
            session.commit()
            session.refresh(proj)
        project_id = proj.id
        _status_data["project_name"] = proj.name
    else:
        proj = session.query(Project).filter(Project.id == project_id).first()
        if proj:
            _status_data["project_name"] = proj.name
    session.close()

    subscribe(str(project_id), _event_handler)

    manager = OrchestratorManager(project_id)

    with Live(_build_table(), refresh_per_second=4, console=console) as live:
        def live_update(payload):
            _event_handler(payload)
            live.update(_build_table())

        subscribe(str(project_id), live_update)
        manager.submit_task(description)

    console.print(f"\n[green]✓ Task complete![/] Check artifacts in projects/project_{project_id}/")


@cli.command()
def web(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    from ui.web_app import app
    init_db()
    console.print(f"[green]Starting web dashboard at http://{host}:{port}[/]")
    uvicorn.run(app, host=host, port=port)
