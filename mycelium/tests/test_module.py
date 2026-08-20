from syzygy_mycelium.module import mycelium_descriptor


def test_mycelium_descriptor() -> None:
    descriptor = mycelium_descriptor("0.1.0")

    assert descriptor.name == "mycelium"
    assert descriptor.version == "0.1.0"
    assert descriptor.status == "online"
    assert descriptor.health.status == "ok"
    assert descriptor.health.details == {"agent": "hypha"}
    assert descriptor.dependencies == ["foundation"]
    assert "foundation_registration" in descriptor.capabilities
    assert "local_node_descriptor" in descriptor.capabilities
    assert "local_peer_registry" in descriptor.capabilities
    assert "mesh_bootstrap" in descriptor.capabilities
