from fastapi import FastAPI

from routers.admin import router as admin_router
from routers.agents import router as agents_router
from routers.architect import router as architect_router
from routers.builder import router as builder_router
from routers.documentation import router as documentation_router
from routers.engine import router as engine_router
from routers.errors import router as errors_router
from routers.github import router as github_router
from routers.health_extra import router as health_extra_router
from routers.metrics import router as metrics_router
from routers.projects import router as projects_router
from routers.sap import router as sap_router
from routers.skills import router as skills_router
from routers.system import router as system_router
from routers.websocket import router as websocket_router
from routers.workflow import router as workflow_router
from routers.transparency import router as transparency_router


def register_routers(app: FastAPI) -> None:
    app.include_router(agents_router)
    app.include_router(system_router)
    app.include_router(architect_router)
    app.include_router(projects_router)
    app.include_router(builder_router)
    app.include_router(engine_router)
    app.include_router(skills_router)
    app.include_router(documentation_router)
    app.include_router(github_router)
    app.include_router(metrics_router)
    app.include_router(sap_router)
    app.include_router(admin_router)
    app.include_router(websocket_router)
    app.include_router(workflow_router)
    app.include_router(errors_router)
    app.include_router(health_extra_router)
    app.include_router(transparency_router)
