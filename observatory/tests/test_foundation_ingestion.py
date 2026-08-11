import httpx
import pytest

from syzygy_observatory.database import Database
from syzygy_observatory.foundation_client import FoundationClient
from syzygy_observatory.foundation_ingestion import (
    FoundationModuleIngestionError,
    FoundationModuleIngestor,
    FoundationModuleIngestRequest,
)
from syzygy_observatory.health_observations import HealthObservationStore


def build_store() -> HealthObservationStore:
    database = Database("sqlite:///:memory:")
    database.initialize()
    return HealthObservationStore(database)


def build_client() -> FoundationClient:
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


@pytest.mark.asyncio
async def test_foundation_module_ingestor_requires_confirmation() -> None:
    ingestor = FoundationModuleIngestor(build_client(), build_store())

    with pytest.raises(FoundationModuleIngestionError, match="confirm=true"):
        await ingestor.ingest(FoundationModuleIngestRequest(confirm=False))


@pytest.mark.asyncio
async def test_foundation_module_ingestor_records_module_health() -> None:
    store = build_store()
    ingestor = FoundationModuleIngestor(build_client(), store)

    result = await ingestor.ingest(FoundationModuleIngestRequest(confirm=True))
    summary = store.summary()

    assert result.observed == 2
    assert [(record.name, record.status) for record in result.observations] == [
        ("foundation", "ok"),
        ("forge", "warning"),
    ]
    assert summary.by_status == {"ok": 1, "warning": 1}
    latest_by_name = {record.name: record for record in summary.latest_by_name}
    assert latest_by_name["forge"].details["module_status"] == "degraded"
    assert latest_by_name["forge"].details["outbox"] == "failed"
