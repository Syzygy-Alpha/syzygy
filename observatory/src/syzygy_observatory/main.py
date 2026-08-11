import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from syzygy_observatory.config import Settings, get_settings
from syzygy_observatory.database import Database
from syzygy_observatory.foundation_client import FoundationClient
from syzygy_observatory.health_observations import (
    HealthObservationRecord,
    HealthObservationRequest,
    HealthObservationStore,
    HealthObservationSummary,
)
from syzygy_observatory.module import ModuleDescriptor, observatory_descriptor

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    logging.basicConfig(level=app_settings.log_level.upper())

    descriptor = observatory_descriptor(app_settings.version)
    database = Database(app_settings.database_url)
    health_observations = HealthObservationStore(database)

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
                logger.info("observatory_registered_with_foundation")
            except Exception:
                logger.exception("observatory_registration_failed")
        yield

    app = FastAPI(
        title="SYZYGY Observatory",
        version=app_settings.version,
        lifespan=lifespan,
    )
    app.state.settings = app_settings
    app.state.descriptor = descriptor
    app.state.database = database
    app.state.health_observations = health_observations

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

    @app.post("/health-observations", status_code=201)
    def record_health_observation(
        request: HealthObservationRequest,
    ) -> HealthObservationRecord:
        return health_observations.record(request)

    @app.get("/health-observations")
    def list_health_observations(
        name: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[HealthObservationRecord]:
        return health_observations.list_observations(name=name, status=status, limit=limit)

    @app.get("/health-observations/summary")
    def health_observation_summary() -> HealthObservationSummary:
        return health_observations.summary()

    return app


app = create_app()
