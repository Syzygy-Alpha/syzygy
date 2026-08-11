from datetime import UTC, datetime

import pytest

from syzygy_forge.database import Database
from syzygy_forge.event_outbox import (
    EventOutboxRecordNotFoundError,
    EventOutboxStatusError,
    ForgeEventOutbox,
)
from syzygy_forge.events import CommandRunEventFactory
from syzygy_forge.project_command_history import ProjectCommandRunRecord


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


def test_event_outbox_enqueues_forge_event() -> None:
    outbox = build_outbox()
    event = CommandRunEventFactory().started(build_command_run_record())

    record = outbox.enqueue(event)

    assert record.id == 1
    assert record.event_id == event.id
    assert record.name == "CommandRunStarted"
    assert record.subject == "syzygy.forge.CommandRunStarted"
    assert record.status == "pending"
    assert record.payload["run_id"] == 1


def test_event_outbox_lists_events_by_status() -> None:
    outbox = build_outbox()
    factory = CommandRunEventFactory()
    run_record = build_command_run_record()
    outbox.enqueue(factory.started(run_record))
    outbox.enqueue(factory.completed(run_record), status="published")

    pending = outbox.list_events("pending")
    all_events = outbox.list_events()

    assert [record.name for record in pending] == ["CommandRunStarted"]
    assert [record.name for record in all_events] == [
        "CommandRunStarted",
        "CommandRunCompleted",
    ]


def test_event_outbox_summary_reports_empty_state() -> None:
    outbox = build_outbox()

    summary = outbox.summary()

    assert summary.total == 0
    assert summary.pending == 0
    assert summary.published == 0
    assert summary.failed == 0
    assert summary.by_status == {}
    assert summary.total_attempts == 0
    assert summary.max_attempts == 0
    assert summary.delivery_status == "ok"
    assert summary.oldest_pending is None
    assert summary.latest_failed is None


def test_event_outbox_summary_reports_delivery_state() -> None:
    outbox = build_outbox()
    factory = CommandRunEventFactory()
    run_record = build_command_run_record()
    first, second = outbox.enqueue_many(
        [factory.started(run_record), factory.completed(run_record)]
    )
    outbox.mark_failed(second.id, "transport unavailable")

    summary = outbox.summary()

    assert summary.total == 2
    assert summary.pending == 1
    assert summary.published == 0
    assert summary.failed == 1
    assert summary.by_status == {"failed": 1, "pending": 1}
    assert summary.total_attempts == 1
    assert summary.max_attempts == 1
    assert summary.delivery_status == "attention"
    assert summary.oldest_pending is not None
    assert summary.oldest_pending.id == first.id
    assert summary.latest_failed is not None
    assert summary.latest_failed.id == second.id


def test_event_outbox_summary_reports_published_state() -> None:
    outbox = build_outbox()
    event = CommandRunEventFactory().started(build_command_run_record())
    record = outbox.enqueue(event)
    outbox.mark_published(record.id)

    summary = outbox.summary()

    assert summary.total == 1
    assert summary.pending == 0
    assert summary.published == 1
    assert summary.failed == 0
    assert summary.by_status == {"published": 1}
    assert summary.total_attempts == 1
    assert summary.max_attempts == 1
    assert summary.delivery_status == "ok"
    assert summary.oldest_pending is None
    assert summary.latest_failed is None


def test_event_outbox_tracks_publish_state() -> None:
    outbox = build_outbox()
    event = CommandRunEventFactory().started(build_command_run_record())
    record = outbox.enqueue(event)

    published = outbox.mark_published(record.id)

    assert published.status == "published"
    assert published.attempts == 1
    assert published.last_error is None
    assert published.published_at is not None
    assert outbox.pending() == []


def test_event_outbox_tracks_publish_failure() -> None:
    outbox = build_outbox()
    event = CommandRunEventFactory().started(build_command_run_record())
    record = outbox.enqueue(event)

    failed = outbox.mark_failed(record.id, "transport unavailable")

    assert failed.status == "failed"
    assert failed.attempts == 1
    assert failed.last_error == "transport unavailable"
    assert failed.published_at is None
    assert outbox.pending() == []


def test_event_outbox_requeues_failed_event() -> None:
    outbox = build_outbox()
    event = CommandRunEventFactory().started(build_command_run_record())
    record = outbox.enqueue(event)
    outbox.mark_failed(record.id, "transport unavailable")

    requeued = outbox.requeue(record.id)

    assert requeued.status == "pending"
    assert requeued.attempts == 1
    assert requeued.last_error is None
    assert requeued.published_at is None
    assert [event.id for event in outbox.pending()] == [record.id]


def test_event_outbox_requeues_failed_events_with_limit() -> None:
    outbox = build_outbox()
    factory = CommandRunEventFactory()
    run_record = build_command_run_record()
    first, second = outbox.enqueue_many(
        [factory.started(run_record), factory.completed(run_record)]
    )
    outbox.mark_failed(first.id, "first failure")
    outbox.mark_failed(second.id, "second failure")

    requeued = outbox.requeue_failed(limit=1)

    assert [record.id for record in requeued] == [first.id]
    assert [record.id for record in outbox.failed()] == [second.id]
    assert [record.id for record in outbox.pending()] == [first.id]


def test_event_outbox_requeue_rejects_missing_event() -> None:
    outbox = build_outbox()

    with pytest.raises(EventOutboxRecordNotFoundError) as exc_info:
        outbox.requeue(404)

    assert "404" in str(exc_info.value)


def test_event_outbox_requeue_rejects_non_failed_event() -> None:
    outbox = build_outbox()
    event = CommandRunEventFactory().started(build_command_run_record())
    record = outbox.enqueue(event)

    with pytest.raises(EventOutboxStatusError) as exc_info:
        outbox.requeue(record.id)

    assert str(record.id) in str(exc_info.value)
