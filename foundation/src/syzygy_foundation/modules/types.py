from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ModuleStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    STARTING = "starting"
    STOPPED = "stopped"
    DEGRADED = "degraded"


class ModuleHealth(BaseModel):
    status: str
    details: dict[str, str] = Field(default_factory=dict)


class ModuleDescriptor(BaseModel):
    name: str
    version: str
    status: ModuleStatus
    health: ModuleHealth
    capabilities: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    last_seen_at: datetime | None = None


class ModuleRegistration(BaseModel):
    name: str
    version: str
    status: ModuleStatus = ModuleStatus.ONLINE
    health: ModuleHealth = Field(default_factory=lambda: ModuleHealth(status="ok"))
    capabilities: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class ModuleStatusUpdate(BaseModel):
    status: ModuleStatus


class ModuleHealthUpdate(BaseModel):
    health: ModuleHealth
