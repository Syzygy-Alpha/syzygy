from typing import Any

from syzygy_foundation.events.bus import EventBus
from syzygy_foundation.persistence import Database


class HealthService:
    def __init__(self, database: Database, event_bus: EventBus) -> None:
        self.database = database
        self.event_bus = event_bus

    def check(self) -> dict[str, Any]:
        database_ok = self.database.ping()
        event_bus_ok = self.event_bus.connected
        status = "ok" if database_ok and event_bus_ok else "degraded"
        return {
            "status": status,
            "checks": {
                "database": "ok" if database_ok else "error",
                "event_bus": "ok" if event_bus_ok else "degraded",
            },
        }

