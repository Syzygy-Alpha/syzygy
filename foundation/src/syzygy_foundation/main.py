import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from syzygy_foundation.config import Settings, get_settings
from syzygy_foundation.events import EventName, FoundationEvent, InMemoryEventBus, NatsEventBus
from syzygy_foundation.logging import configure_logging
from syzygy_foundation.modules import ModuleDescriptor, ModuleHealth, ModuleRegistry, ModuleStatus
from syzygy_foundation.persistence import Database
from syzygy_foundation.scheduler import Scheduler

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    configure_logging(app_settings.log_level)

    database = Database(app_settings.database_url)
    event_bus = (
        NatsEventBus(app_settings.nats_url) if app_settings.nats_enabled else InMemoryEventBus()
    )
    scheduler = Scheduler()
    module_registry = ModuleRegistry()
    foundation_capabilities = [
        "configuration",
        "health",
        "version",
        "authentication",
        "event_bus",
        "scheduler",
        "persistence",
        "module_lifecycle",
    ]
    foundation_dependencies = [
        "sqlite",
        "nats" if app_settings.nats_enabled else "in_memory_event_bus",
    ]

    module_registry.register(
        ModuleDescriptor(
            name="foundation",
            version=app_settings.version,
            status=ModuleStatus.STARTING,
            health=ModuleHealth(status="starting"),
            capabilities=foundation_capabilities,
            dependencies=foundation_dependencies,
        )
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        logger.info("foundation_starting")
        database.initialize()
        try:
            await event_bus.connect()
        except Exception:
            logger.exception("event_bus_connection_failed")
        await scheduler.start()
        module_registry.register(
            ModuleDescriptor(
                name="foundation",
                version=app_settings.version,
                status=ModuleStatus.ONLINE,
                health=ModuleHealth(status="ok"),
                capabilities=foundation_capabilities,
                dependencies=foundation_dependencies,
            )
        )
        if event_bus.connected:
            await event_bus.publish(
                FoundationEvent(
                    name=EventName.MODULE_STARTED,
                    producer=app_settings.service_name,
                    payload={"module": "foundation", "version": app_settings.version},
                )
            )
        try:
            yield
        finally:
            if event_bus.connected:
                await event_bus.publish(
                    FoundationEvent(
                        name=EventName.MODULE_STOPPED,
                        producer=app_settings.service_name,
                        payload={"module": "foundation"},
                    )
                )
            await scheduler.stop()
            await event_bus.close()
            logger.info("foundation_stopped")

    app = FastAPI(
        title="SYZYGY Foundation",
        version=app_settings.version,
        lifespan=lifespan,
    )
    app.state.settings = app_settings
    app.state.database = database
    app.state.event_bus = event_bus
    app.state.scheduler = scheduler
    app.state.module_registry = module_registry

    from syzygy_foundation.api import create_router

    app.include_router(create_router())
    return app


app = create_app()
