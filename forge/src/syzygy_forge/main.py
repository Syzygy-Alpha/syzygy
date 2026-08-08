import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from syzygy_forge.config import Settings, get_settings
from syzygy_forge.foundation_client import FoundationClient
from syzygy_forge.module import ModuleDescriptor, forge_descriptor
from syzygy_forge.project_inspector import ProjectInspection, ProjectInspector

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    logging.basicConfig(level=app_settings.log_level.upper())

    descriptor = forge_descriptor(app_settings.version)
    project_inspector = ProjectInspector()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
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
    app.state.project_inspector = project_inspector

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

    return app


app = create_app()
