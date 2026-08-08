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


FORGE_CAPABILITIES = [
    "git",
    "project_creation",
    "project_inspection",
    "project_templates",
    "local_workflows",
]


def forge_descriptor(version: str, status: str = "online") -> ModuleDescriptor:
    return ModuleDescriptor(
        name="forge",
        version=version,
        status=status,
        health=ModuleHealth(status="ok"),
        capabilities=FORGE_CAPABILITIES,
        dependencies=["foundation"],
    )
