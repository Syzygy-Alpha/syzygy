import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from syzygy_observatory.config import Settings, get_settings
from syzygy_observatory.database import Database
from syzygy_observatory.foundation_client import FoundationClient
from syzygy_observatory.foundation_ingestion import (
    FoundationModuleIngestionError,
    FoundationModuleIngestor,
    FoundationModuleIngestRequest,
    FoundationModuleIngestResult,
)
from syzygy_observatory.foundation_polling import (
    FoundationModulePoller,
    FoundationModulePollingStatus,
)
from syzygy_observatory.health_observations import (
    HealthObservationRecord,
    HealthObservationRequest,
    HealthObservationStore,
    HealthObservationSummary,
    HealthObservationTrends,
)
from syzygy_observatory.module import ModuleDescriptor, observatory_descriptor

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    logging.basicConfig(level=app_settings.log_level.upper())

    descriptor = observatory_descriptor(app_settings.version)
    database = Database(app_settings.database_url)
    health_observations = HealthObservationStore(database)
    foundation_client = FoundationClient(
        base_url=app_settings.foundation_url,
        username=app_settings.foundation_username,
        password=app_settings.foundation_password.get_secret_value(),
    )
    foundation_module_ingestor = FoundationModuleIngestor(
        foundation_client=foundation_client,
        health_observations=health_observations,
    )
    foundation_module_poller = FoundationModulePoller(
        ingestor=foundation_module_ingestor,
        enabled=app_settings.foundation_module_polling_enabled,
        interval_seconds=app_settings.foundation_module_polling_interval_seconds,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database.initialize()
        if app_settings.register_with_foundation:
            try:
                await foundation_client.register_module(descriptor)
                logger.info("observatory_registered_with_foundation")
            except Exception:
                logger.exception("observatory_registration_failed")
        if app_settings.foundation_module_polling_enabled:
            foundation_module_poller.start()
            logger.info("foundation_module_polling_started")
        try:
            yield
        finally:
            await foundation_module_poller.stop()

    app = FastAPI(
        title="SYZYGY Observatory",
        version=app_settings.version,
        lifespan=lifespan,
    )
    app.state.settings = app_settings
    app.state.descriptor = descriptor
    app.state.database = database
    app.state.health_observations = health_observations
    app.state.foundation_client = foundation_client
    app.state.foundation_module_ingestor = foundation_module_ingestor
    app.state.foundation_module_poller = foundation_module_poller

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

    @app.get("/health-observations/trends")
    def health_observation_trends(name: str | None = None) -> HealthObservationTrends:
        return health_observations.trends(name=name)

    @app.post("/ingest/foundation/modules")
    async def ingest_foundation_modules(
        request: FoundationModuleIngestRequest,
    ) -> FoundationModuleIngestResult:
        try:
            return await foundation_module_ingestor.ingest(request)
        except FoundationModuleIngestionError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get("/ingest/foundation/modules/polling")
    def foundation_module_polling_status() -> FoundationModulePollingStatus:
        return foundation_module_poller.status()

    return app


app = create_app()
