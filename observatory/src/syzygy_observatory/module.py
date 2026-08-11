from pydantic import BaseModel, Field


class ModuleHealth(BaseModel):
    status: str
    details: dict[str, str] = Field(default_factory=dict)


class ModuleDescriptor(BaseModel):
    name: str
    version: str
    status: str
    health: ModuleHealth
    capabilities: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


OBSERVATORY_CAPABILITIES = [
    "foundation_module_ingestion",
    "health_observation_storage",
    "health_summary",
    "local_observability",
]


def observatory_descriptor(version: str, status: str = "online") -> ModuleDescriptor:
    return ModuleDescriptor(
        name="observatory",
        version=version,
        status=status,
        health=ModuleHealth(status="ok"),
        capabilities=OBSERVATORY_CAPABILITIES,
        dependencies=["foundation"],
    )
