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


NERV_CAPABILITIES = [
    "dashboard",
    "surface_catalog",
    "module_launcher",
    "module_monitoring",
]


def nerv_descriptor(version: str, status: str = "online") -> ModuleDescriptor:
    return ModuleDescriptor(
        name="nerv",
        version=version,
        status=status,
        health=ModuleHealth(status="ok", details={"mode": "local_command_center"}),
        capabilities=NERV_CAPABILITIES,
        dependencies=["foundation", "forge", "observatory", "mycelium"],
    )
