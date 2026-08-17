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


MYCELIUM_CAPABILITIES = [
    "foundation_registration",
    "local_node_descriptor",
    "mesh_bootstrap",
]


def mycelium_descriptor(version: str, status: str = "online") -> ModuleDescriptor:
    return ModuleDescriptor(
        name="mycelium",
        version=version,
        status=status,
        health=ModuleHealth(status="ok", details={"agent": "hypha"}),
        capabilities=MYCELIUM_CAPABILITIES,
        dependencies=["foundation"],
    )
