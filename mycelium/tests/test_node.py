from syzygy_mycelium.node import local_node_descriptor


def test_local_node_descriptor() -> None:
    node = local_node_descriptor("desktop", "Desktop")

    assert node.node_id == "desktop"
    assert node.name == "Desktop"
    assert node.agent == "hypha"
    assert node.status == "online"
    assert "local_identity" in node.capabilities
