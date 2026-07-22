from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from core.event_bus import stream, publish
from core.manager import OrchestratorManager
from storage.db import get_session, init_db
from storage.models import Project, Task, Artifact, ProjectStatus

app = FastAPI(title="AI Orchestrator")

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.get("/projects")
def list_projects():
    session = get_session()
    projects = session.query(Project).order_by(Project.created_at.desc()).all()
    result = []
    for p in projects:
        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "status": p.status.value,
            "task_count": len(p.tasks),
            "created_at": str(p.created_at)[:19],
        })
    session.close()
    return result


@app.post("/projects")
def create_project(name: str, description: str = ""):
    init_db()
    session = get_session()
    proj = Project(name=name, description=description)
    session.add(proj)
    session.commit()
    session.refresh(proj)
    session.close()
    return {"id": proj.id, "name": proj.name}


@app.get("/projects/{project_id}", response_class=HTMLResponse)
def project_detail(request: Request, project_id: int):
    return templates.TemplateResponse(request, "project.html", {"request": request, "project_id": project_id})


@app.get("/projects/{project_id}/data")
def project_data(project_id: int):
    session = get_session()
    proj = session.query(Project).filter(Project.id == project_id).first()
    if not proj:
        session.close()
        return {"error": "Not found"}
    tasks = []
    for t in proj.tasks:
        tasks.append({
            "id": t.id,
            "title": t.title,
            "status": t.status.value,
            "agent": t.assigned_agent,
            "category": t.category,
            "result": (t.result or "")[:500],
        })
    artifacts = []
    for a in session.query(Artifact).join(Task).filter(Task.project_id == project_id).all():
        artifacts.append({"path": a.file_path, "type": a.artifact_type})
    session.close()
    return {
        "id": proj.id,
        "name": proj.name,
        "description": proj.description,
        "status": proj.status.value,
        "created_at": str(proj.created_at)[:19],
        "tasks": tasks,
        "artifacts": artifacts,
    }


@app.post("/projects/{project_id}/tasks")
async def submit_task(project_id: int, description: str, title: str = ""):
    init_db()
    manager = OrchestratorManager(project_id)
    task = manager.submit_task(description, title=title)
    return {"task_id": task.id, "status": "completed"}


@app.get("/projects/{project_id}/stream")
async def event_stream(project_id: int):
    return StreamingResponse(
        stream(str(project_id)),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/projects/{project_id}/artifacts")
def list_artifacts(project_id: int):
    session = get_session()
    artifacts = (
        session.query(Artifact)
        .join(Task)
        .filter(Task.project_id == project_id)
        .all()
    )
    result = [{"path": a.file_path, "type": a.artifact_type, "description": a.description} for a in artifacts]
    session.close()
    return result
