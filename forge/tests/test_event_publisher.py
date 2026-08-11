from datetime import UTC, datetime

import pytest

from syzygy_forge.database import Database
from syzygy_forge.event_outbox import ForgeEventOutbox, ForgeEventOutboxRecord
from syzygy_forge.event_publisher import (
    EventOutboxPublisher,
    EventPublishingError,
    EventPublishRequest,
    InMemoryEventPublisher,
)
from syzygy_forge.events import CommandRunEventFactory
from syzygy_forge.project_command_history import ProjectCommandRunRecord


class FailingEventPublisher:
    async def publish(self, record: ForgeEventOutboxRecord) -> None:
        msg = f"failed to publish {record.event_id}"
        raise RuntimeError(msg)


def build_outbox() -> ForgeEventOutbox:
    database = Database("sqlite:///:memory:")
    database.initialize()
    return ForgeEventOutbox(database)


def build_command_run_record() -> ProjectCommandRunRecord:
    return ProjectCommandRunRecord(
        id=1,
        project="hello-tool",
        command_name="test",
        command="python -m pytest",
        cwd="C:/workspace/hello-tool",
        allowed=True,
        reason="allowed",
        returncode=0,
        timed_out=False,
        started_at=datetime(2026, 8, 8, 0, 0, 0, tzinfo=UTC),
        completed_at=datetime(2026, 8, 8, 0, 0, 3, tzinfo=UTC),
    )


@pytest.mark.asyncio
async def test_event_outbox_publisher_requires_confirmation() -> None:
    outbox = build_outbox()
    publisher = EventOutboxPublisher(outbox, InMemoryEventPublisher())

    with pytest.raises(EventPublishingError, match="confirm=true"):
        await publisher.publish_pending(EventPublishRequest(confirm=False))


@pytest.mark.asyncio
async def test_event_outbox_publisher_marks_pending_events_published() -> None:
    outbox = build_outbox()
    transport = InMemoryEventPublisher()
    publisher = EventOutboxPublisher(outbox, transport)
    factory = CommandRunEventFactory()
    run_record = build_command_run_record()
    outbox.enqueue_many([factory.started(run_record), factory.completed(run_record)])

    result = await publisher.publish_pending(EventPublishRequest(confirm=True))

    assert result.attempted == 2
    assert result.published == 2
    assert result.failed == 0
    assert [record.name for record in transport.published] == [
        "CommandRunStarted",
        "CommandRunCompleted",
    ]
    assert [record.status for record in outbox.list_events()] == ["published", "published"]


@pytest.mark.asyncio
async def test_event_outbox_publisher_marks_failures() -> None:
    outbox = build_outbox()
    publisher = EventOutboxPublisher(outbox, FailingEventPublisher())
    event = CommandRunEventFactory().started(build_command_run_record())
    outbox.enqueue(event)

    result = await publisher.publish_pending(EventPublishRequest(confirm=True))

    [failure] = result.failures
    [stored] = outbox.list_events()
    assert result.attempted == 1
    assert result.published == 0
    assert result.failed == 1
    assert failure.event_id == event.id
    assert stored.status == "failed"
    assert stored.attempts == 1
    assert stored.last_error == f"failed to publish {event.id}"
