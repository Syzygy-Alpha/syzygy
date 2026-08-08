from collections.abc import Awaitable, Callable
from typing import Protocol

from syzygy_foundation.events.catalog import FoundationEvent

EventHandler = Callable[[FoundationEvent], Awaitable[None]]


class EventBus(Protocol):
    @property
    def connected(self) -> bool:
        raise NotImplementedError

    async def connect(self) -> None:
        raise NotImplementedError

    async def close(self) -> None:
        raise NotImplementedError

    async def publish(self, event: FoundationEvent) -> None:
        raise NotImplementedError

    async def subscribe(self, event_name: str, handler: EventHandler) -> None:
        raise NotImplementedError


class InMemoryEventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}
        self._connected = False
        self.published_events: list[FoundationEvent] = []

    @property
    def connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        self._connected = True

    async def close(self) -> None:
        self._connected = False

    async def publish(self, event: FoundationEvent) -> None:
        self.published_events.append(event)
        for handler in self._handlers.get(event.name.value, []):
            await handler(event)

    async def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._handlers.setdefault(event_name, []).append(handler)

