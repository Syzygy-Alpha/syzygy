import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from syzygy_mycelium.config import Settings, get_settings
from syzygy_mycelium.database import Database
from syzygy_mycelium.foundation_client import FoundationClient
from syzygy_mycelium.module import ModuleDescriptor, mycelium_descriptor
from syzygy_mycelium.node import NodeDescriptor, local_node_descriptor
from syzygy_mycelium.peer_registry import (
    PeerRecord,
    PeerRegistrationRequest,
    PeerRegistry,
    PeerRegistryError,
)

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    logging.basicConfig(level=app_settings.log_level.upper())

    descriptor = mycelium_descriptor(app_settings.version)
    database = Database(app_settings.database_url)
    peer_registry = PeerRegistry(database)
    node = local_node_descriptor(app_settings.node_id, app_settings.node_name)
    foundation_client = FoundationClient(
        base_url=app_settings.foundation_url,
        username=app_settings.foundation_username,
        password=app_settings.foundation_password.get_secret_value(),
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database.initialize()
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
    app.state.database = database
    app.state.peer_registry = peer_registry
    app.state.node = node
    app.state.foundation_client = foundation_client

    @app.get("/")
    def root() -> dict[str, str]:
        return {"name": app_settings.service_name, "status": "ok"}

    @app.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "checks": {
                "module": "ok",
                "node": node.status,
                "peer_registry": "ok",
            },
        }

    @app.get("/version")
    def version() -> dict[str, str]:
        return {"name": app_settings.service_name, "version": app_settings.version}

    @app.get("/capabilities")
    def capabilities() -> ModuleDescriptor:
        return descriptor

    @app.get("/node")
    def local_node() -> NodeDescriptor:
        return node

    @app.get("/peers")
    def list_peers() -> list[PeerRecord]:
        return peer_registry.list_peers()

    @app.post("/peers")
    def register_peer(request: PeerRegistrationRequest) -> PeerRecord:
        try:
            return peer_registry.register(request)
        except PeerRegistryError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/peers/{node_id}")
    def get_peer(node_id: str) -> PeerRecord:
        peer = peer_registry.get(node_id)
        if peer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peer not found")
        return peer

    return app


app = create_app()
