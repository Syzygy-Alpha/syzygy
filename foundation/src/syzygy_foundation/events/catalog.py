from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EventName(StrEnum):
    MODULE_STARTED = "ModuleStarted"
    MODULE_STOPPED = "ModuleStopped"
    CONFIG_UPDATED = "ConfigUpdated"
    HEALTH_CHANGED = "HealthChanged"


class FoundationEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: EventName
    producer: str
    payload: dict[str, Any] = Field(default_factory=dict)
    version: str = "1.0"
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def subject(self) -> str:
        return f"syzygy.foundation.{self.name.value}"
