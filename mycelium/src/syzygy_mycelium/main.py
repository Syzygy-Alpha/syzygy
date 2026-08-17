import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from syzygy_mycelium.config import Settings, get_settings
from syzygy_mycelium.foundation_client import FoundationClient
from syzygy_mycelium.module import ModuleDescriptor, mycelium_descriptor
from syzygy_mycelium.node import NodeDescriptor, local_node_descriptor

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    logging.basicConfig(level=app_settings.log_level.upper())

    descriptor = mycelium_descriptor(app_settings.version)
    node = local_node_descriptor(app_settings.node_id, app_settings.node_name)
    foundation_client = FoundationClient(
        base_url=app_settings.foundation_url,
        username=app_settings.foundation_username,
        password=app_settings.foundation_password.get_secret_value(),
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if app_settings.register_with_foundation:
            try:
                await foundation_client.register_module(descriptor)
                logger.info("mycelium_registered_with_foundation")
            except Exception:
                logger.exception("mycelium_registration_failed")
        yield

    app = FastAPI(title="SYZYGY Mycelium", version=app_settings.version, lifespan=lifespan)
    app.state.settings = app_settings
    app.state.descriptor = descriptor
    app.state.node = node
    app.state.foundation_client = foundation_client

    @app.get("/")
    def root() -> dict[str, str]:
        return {"name": app_settings.service_name, "status": "ok"}

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "checks": {"module": "ok", "node": node.status}}

    @app.get("/version")
    def version() -> dict[str, str]:
        return {"name": app_settings.service_name, "version": app_settings.version}

    @app.get("/capabilities")
    def capabilities() -> ModuleDescriptor:
        return descriptor

    @app.get("/node")
    def local_node() -> NodeDescriptor:
        return node

    return app


app = create_app()
