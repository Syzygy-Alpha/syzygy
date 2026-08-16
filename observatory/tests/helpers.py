import httpx

from syzygy_observatory.database import Database
from syzygy_observatory.foundation_client import FoundationClient
from syzygy_observatory.health_observations import HealthObservationStore


def build_store() -> HealthObservationStore:
    database = Database("sqlite:///:memory:")
    database.initialize()
    return HealthObservationStore(database)


def build_foundation_client() -> FoundationClient:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/auth/token":
            return httpx.Response(200, json={"access_token": "token"})
        if request.url.path == "/modules":
            return httpx.Response(
                200,
                json=[
                    {
                        "name": "foundation",
                        "version": "0.1.0",
                        "status": "online",
                        "health": {"status": "ok", "details": {"database": "ok"}},
                        "capabilities": ["module_lifecycle"],
                        "dependencies": ["sqlite"],
                    },
                    {
                        "name": "forge",
                        "version": "0.1.0",
                        "status": "degraded",
                        "health": {"status": "warning", "details": {"outbox": "failed"}},
                        "capabilities": ["git"],
                        "dependencies": ["foundation"],
                    },
                ],
            )
        return httpx.Response(404)

    return FoundationClient(
        base_url="http://foundation.test",
        username="admin",
        password="secret",
        transport=httpx.MockTransport(handler),
    )
