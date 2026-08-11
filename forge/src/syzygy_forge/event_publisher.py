import json
from typing import Any, Protocol

import nats
from pydantic import BaseModel, Field

from syzygy_forge.event_outbox import ForgeEventOutbox, ForgeEventOutboxRecord


class EventPublisher(Protocol):
    async def publish(self, record: ForgeEventOutboxRecord) -> None:
        raise NotImplementedError


class InMemoryEventPublisher:
    def __init__(self) -> None:
        self.published: list[ForgeEventOutboxRecord] = []

    async def publish(self, record: ForgeEventOutboxRecord) -> None:
        self.published.append(record)


class NatsEventPublisher:
    def __init__(self, url: str) -> None:
        self.url = url
        self._client: Any | None = None

    async def publish(self, record: ForgeEventOutboxRecord) -> None:
        if self._client is None or not self._client.is_connected:
            self._client = await nats.connect(self.url)
        await self._client.publish(record.subject, self._payload(record))

    def _payload(self, record: ForgeEventOutboxRecord) -> bytes:
        return json.dumps(
            {
                "id": record.event_id,
                "name": record.name,
                "producer": record.producer,
                "payload": record.payload,
                "version": record.version,
                "occurred_at": record.occurred_at.isoformat(),
            }
        ).encode("utf-8")


class EventPublishRequest(BaseModel):
    confirm: bool = Field(default=False)
    limit: int = Field(default=100, ge=1, le=500)


class EventPublishFailure(BaseModel):
    id: int
    event_id: str
    error: str


class EventPublishResult(BaseModel):
    attempted: int
    published: int
    failed: int
    failures: list[EventPublishFailure] = Field(default_factory=list)


class EventPublishingError(ValueError):
    pass


class EventOutboxPublisher:
    def __init__(self, outbox: ForgeEventOutbox, publisher: EventPublisher) -> None:
        self.outbox = outbox
        self.publisher = publisher

    async def publish_pending(self, request: EventPublishRequest) -> EventPublishResult:
        if not request.confirm:
            msg = "Event publishing requires confirm=true"
            raise EventPublishingError(msg)

        records = self.outbox.pending(request.limit)
        published = 0
        failures: list[EventPublishFailure] = []
        for record in records:
            try:
                await self.publisher.publish(record)
            except Exception as exc:
                error = str(exc)
                self.outbox.mark_failed(record.id, error)
                failures.append(
                    EventPublishFailure(id=record.id, event_id=record.event_id, error=error)
                )
                continue
            self.outbox.mark_published(record.id)
            published += 1

        return EventPublishResult(
            attempted=len(records),
            published=published,
            failed=len(failures),
            failures=failures,
        )


def build_event_publisher(transport: str, nats_url: str) -> EventPublisher:
    if transport == "memory":
        return InMemoryEventPublisher()
    if transport == "nats":
        return NatsEventPublisher(nats_url)
    msg = f"Unsupported event publisher transport: {transport}"
    raise ValueError(msg)
