import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, status

from syzygy_forge.config import Settings, get_settings
from syzygy_forge.database import Database
from syzygy_forge.foundation_client import FoundationClient
from syzygy_forge.module import ModuleDescriptor, forge_descriptor
from syzygy_forge.project_creator import (
    ProjectCreationError,
    ProjectCreationRequest,
    ProjectCreationResult,
    ProjectCreator,
)
from syzygy_forge.project_inspector import ProjectInspection, ProjectInspector
from syzygy_forge.project_registry import (
    ProjectDetails,
    ProjectPathError,
    ProjectRecord,
    ProjectRegistrationRequest,
    ProjectRegistry,
)
from syzygy_forge.project_templates import (
    ProjectTemplate,
    get_project_template,
    list_project_templates,
)

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    logging.basicConfig(level=app_settings.log_level.upper())

    descriptor = forge_descriptor(app_settings.version)
    database = Database(app_settings.database_url)
    project_inspector = ProjectInspector()
    project_registry = ProjectRegistry(database)
    project_creator = ProjectCreator(app_settings.workspace_root, project_registry)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database.initialize()
        if app_settings.register_with_foundation:
            client = FoundationClient(
                base_url=app_settings.foundation_url,
                username=app_settings.foundation_username,
                password=app_settings.foundation_password.get_secret_value(),
            )
            try:
                await client.register_module(descriptor)
                logger.info("forge_registered_with_foundation")
            except Exception:
                logger.exception("forge_registration_failed")
        yield

    app = FastAPI(title="SYZYGY Forge", version=app_settings.version, lifespan=lifespan)
    app.state.settings = app_settings
    app.state.descriptor = descriptor
    app.state.database = database
    app.state.project_inspector = project_inspector
    app.state.project_registry = project_registry
    app.state.project_creator = project_creator

    @app.get("/")
    def root() -> dict[str, str]:
        return {"name": app_settings.service_name, "status": "ok"}

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "checks": {"module": "ok"}}

    @app.get("/version")
    def version() -> dict[str, str]:
        return {"name": app_settings.service_name, "version": app_settings.version}

    @app.get("/capabilities")
    def capabilities() -> ModuleDescriptor:
        return descriptor

    @app.get("/projects/current")
    def current_project() -> ProjectInspection:
        return project_inspector.inspect(app_settings.workspace_root)

    @app.get("/project-templates")
    def project_templates() -> list[ProjectTemplate]:
        return list_project_templates()

    @app.get("/project-templates/{name}")
    def get_template(name: str) -> ProjectTemplate:
        template = get_project_template(name)
        if template is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project template not found",
            )
        return template

    @app.post("/projects", status_code=status.HTTP_201_CREATED)
    def register_project(request: ProjectRegistrationRequest) -> ProjectRecord:
        try:
            return project_registry.register(request.path, request.name)
        except ProjectPathError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/projects")
    def list_projects() -> list[ProjectRecord]:
        return project_registry.list_projects()

    @app.post("/projects/create", status_code=status.HTTP_201_CREATED)
    def create_project(request: ProjectCreationRequest) -> ProjectCreationResult:
        try:
            return project_creator.create(request)
        except ProjectCreationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/projects/{name}")
    def get_project(name: str) -> ProjectDetails:
        record = project_registry.get(name)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return ProjectDetails(
            record=record,
            inspection=project_inspector.inspect(Path(record.path)),
        )

    return app


app = create_app()
