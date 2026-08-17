from pydantic import BaseModel, Field


class NodeDescriptor(BaseModel):
    node_id: str
    name: str
    agent: str = "hypha"
    status: str = "online"
    capabilities: list[str] = Field(default_factory=list)


def local_node_descriptor(node_id: str, name: str) -> NodeDescriptor:
    return NodeDescriptor(
        node_id=node_id,
        name=name,
        capabilities=[
            "local_identity",
            "health_reporting",
        ],
    )
