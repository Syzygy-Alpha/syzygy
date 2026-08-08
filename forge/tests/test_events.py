from datetime import UTC, datetime

from syzygy_forge.events import CommandRunEventFactory, ForgeEventName
from syzygy_forge.project_command_history import ProjectCommandRunRecord


def build_record() -> ProjectCommandRunRecord:
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


def test_command_run_started_event_contract() -> None:
    event = CommandRunEventFactory().started(build_record())

    assert event.name == ForgeEventName.COMMAND_RUN_STARTED
    assert event.producer == "forge"
    assert event.subject() == "syzygy.forge.CommandRunStarted"
    assert event.payload["run_id"] == 1
    assert event.payload["project"] == "hello-tool"
    assert event.payload["started_at"] == "2026-08-08T00:00:00+00:00"
    assert "stdout" not in event.payload
    assert "stderr" not in event.payload


def test_command_run_completed_event_contract() -> None:
    event = CommandRunEventFactory().completed(build_record())

    assert event.name == ForgeEventName.COMMAND_RUN_COMPLETED
    assert event.subject() == "syzygy.forge.CommandRunCompleted"
    assert event.payload["returncode"] == 0
    assert event.payload["timed_out"] is False
    assert event.payload["completed_at"] == "2026-08-08T00:00:03+00:00"
    assert "stdout" not in event.payload
    assert "stderr" not in event.payload
