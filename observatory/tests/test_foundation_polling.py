import asyncio

import pytest
from helpers import build_foundation_client, build_store

from syzygy_observatory.foundation_ingestion import FoundationModuleIngestor
from syzygy_observatory.foundation_polling import FoundationModulePoller


@pytest.mark.asyncio
async def test_foundation_module_poller_runs_one_ingestion() -> None:
    store = build_store()
    ingestor = FoundationModuleIngestor(build_foundation_client(), store)
    poller = FoundationModulePoller(ingestor=ingestor, enabled=False, interval_seconds=60)

    result = await poller.poll_once()
    status = poller.status()

    assert result.observed == 2
    assert status.enabled is False
    assert status.running is False
    assert status.last_observed == 2
    assert status.last_error is None
    assert store.summary().total == 2


@pytest.mark.asyncio
async def test_foundation_module_poller_starts_only_when_enabled() -> None:
    store = build_store()
    ingestor = FoundationModuleIngestor(build_foundation_client(), store)
    disabled_poller = FoundationModulePoller(
        ingestor=ingestor,
        enabled=False,
        interval_seconds=60,
    )
    enabled_poller = FoundationModulePoller(
        ingestor=ingestor,
        enabled=True,
        interval_seconds=60,
    )

    disabled_poller.start()
    enabled_poller.start()
    await asyncio.sleep(0)
    await enabled_poller.stop()

    assert disabled_poller.status().running is False
    assert disabled_poller.status().last_observed is None
    assert enabled_poller.status().running is False
    assert enabled_poller.status().last_observed == 2
