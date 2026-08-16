import asyncio
import logging

from pydantic import BaseModel

from syzygy_observatory.foundation_ingestion import (
    FoundationModuleIngestor,
    FoundationModuleIngestRequest,
    FoundationModuleIngestResult,
)


class FoundationModulePollingStatus(BaseModel):
    enabled: bool
    running: bool
    interval_seconds: int
    last_observed: int | None = None
    last_error: str | None = None


class FoundationModulePoller:
    def __init__(
        self,
        ingestor: FoundationModuleIngestor,
        interval_seconds: int,
        enabled: bool = False,
        logger_: logging.Logger | None = None,
    ) -> None:
        if interval_seconds < 1:
            msg = "Foundation module polling interval must be at least 1 second"
            raise ValueError(msg)
        self.ingestor = ingestor
        self.interval_seconds = interval_seconds
        self.enabled = enabled
        self.logger = logger_ or logging.getLogger(__name__)
        self.last_observed: int | None = None
        self.last_error: str | None = None
        self._stop_event: asyncio.Event | None = None
        self._task: asyncio.Task[None] | None = None

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    def status(self) -> FoundationModulePollingStatus:
        return FoundationModulePollingStatus(
            enabled=self.enabled,
            running=self.running,
            interval_seconds=self.interval_seconds,
            last_observed=self.last_observed,
            last_error=self.last_error,
        )

    async def poll_once(self) -> FoundationModuleIngestResult:
        result = await self.ingestor.ingest(FoundationModuleIngestRequest(confirm=True))
        self.last_observed = result.observed
        self.last_error = None
        return result

    def start(self) -> None:
        if not self.enabled or self.running:
            return
        self._stop_event = asyncio.Event()
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._stop_event is not None:
            self._stop_event.set()
        if self._task is not None:
            await self._task
        self._task = None
        self._stop_event = None

    async def _run(self) -> None:
        stop_event = self._stop_event
        if stop_event is None:
            return

        while not stop_event.is_set():
            try:
                result = await self.poll_once()
                self.logger.info(
                    "foundation_module_poll_completed",
                    extra={"observed": result.observed},
                )
            except Exception as exc:
                self.last_error = str(exc)
                self.logger.exception("foundation_module_poll_failed")

            try:
                await asyncio.wait_for(stop_event.wait(), timeout=self.interval_seconds)
            except TimeoutError:
                continue
