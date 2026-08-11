from datetime import UTC, datetime

from syzygy_forge.database import Database
from syzygy_forge.event_outbox import ForgeEventOutbox
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
