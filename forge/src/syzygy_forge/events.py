from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from syzygy_forge.project_command_history import ProjectCommandRunRecord


class ForgeEventName(StrEnum):
    COMMAND_RUN_STARTED = "CommandRunStarted"
    COMMAND_RUN_COMPLETED = "CommandRunCompleted"


class ForgeEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: ForgeEventName
    producer: str = "forge"
    payload: dict[str, Any] = Field(default_factory=dict)
    version: str = "1.0"
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def subject(self) -> str:
        return f"syzygy.forge.{self.name.value}"


class CommandRunEventFactory:
    def started(self, record: ProjectCommandRunRecord) -> ForgeEvent:
        return ForgeEvent(
            name=ForgeEventName.COMMAND_RUN_STARTED,
            occurred_at=record.started_at,
            payload=self._base_payload(record),
        )

    def completed(self, record: ProjectCommandRunRecord) -> ForgeEvent:
        return ForgeEvent(
            name=ForgeEventName.COMMAND_RUN_COMPLETED,
            occurred_at=record.completed_at,
            payload={
                **self._base_payload(record),
                "returncode": record.returncode,
                "timed_out": record.timed_out,
                "completed_at": record.completed_at.isoformat(),
            },
        )

    def _base_payload(self, record: ProjectCommandRunRecord) -> dict[str, Any]:
        return {
            "run_id": record.id,
            "project": record.project,
            "command_name": record.command_name,
            "command": record.command,
            "cwd": record.cwd,
            "allowed": record.allowed,
            "reason": record.reason,
            "started_at": record.started_at.isoformat(),
        }
