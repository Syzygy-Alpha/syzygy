import json
import logging
from typing import Any

import nats

from syzygy_foundation.events.bus import EventHandler
from syzygy_foundation.events.catalog import FoundationEvent

logger = logging.getLogger(__name__)


class NatsEventBus:
    def __init__(self, url: str) -> None:
        self.url = url
        self._client: Any | None = None

    @property
    def connected(self) -> bool:
        return bool(self._client and self._client.is_connected)

    async def connect(self) -> None:
        self._client = await nats.connect(self.url)
        logger.info("event_bus_connected")

    async def close(self) -> None:
        if self._client:
            await self._client.close()
            logger.info("event_bus_closed")

    async def publish(self, event: FoundationEvent) -> None:
        if not self._client:
            msg = "NATS client is not connected"
            raise RuntimeError(msg)
        payload = event.model_dump_json().encode("utf-8")
        await self._client.publish(event.subject(), payload)

    async def subscribe(self, event_name: str, handler: EventHandler) -> None:
        if not self._client:
            msg = "NATS client is not connected"
            raise RuntimeError(msg)

        async def wrapped(message: Any) -> None:
            event = FoundationEvent.model_validate(json.loads(message.data.decode("utf-8")))
            await handler(event)

        await self._client.subscribe(f"syzygy.foundation.{event_name}", cb=wrapped)
