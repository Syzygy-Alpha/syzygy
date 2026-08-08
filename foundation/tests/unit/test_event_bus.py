from syzygy_foundation.events import EventName, FoundationEvent, InMemoryEventBus


async def test_in_memory_event_bus_publishes_to_subscribers() -> None:
    bus = InMemoryEventBus()
    received: list[FoundationEvent] = []

    async def handler(event: FoundationEvent) -> None:
        received.append(event)

    await bus.connect()
    await bus.subscribe(EventName.MODULE_STARTED.value, handler)
    event = FoundationEvent(
        name=EventName.MODULE_STARTED,
        producer="test",
        payload={"module": "foundation"},
    )

    await bus.publish(event)

    assert received == [event]
    assert bus.published_events == [event]

