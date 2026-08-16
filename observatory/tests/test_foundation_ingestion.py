import pytest
from helpers import build_foundation_client, build_store

from syzygy_observatory.foundation_ingestion import (
    FoundationModuleIngestionError,
    FoundationModuleIngestor,
    FoundationModuleIngestRequest,
)


@pytest.mark.asyncio
async def test_foundation_module_ingestor_requires_confirmation() -> None:
    ingestor = FoundationModuleIngestor(build_foundation_client(), build_store())

    with pytest.raises(FoundationModuleIngestionError, match="confirm=true"):
        await ingestor.ingest(FoundationModuleIngestRequest(confirm=False))


@pytest.mark.asyncio
async def test_foundation_module_ingestor_records_module_health() -> None:
    store = build_store()
    ingestor = FoundationModuleIngestor(build_foundation_client(), store)

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
