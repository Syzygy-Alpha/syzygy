from syzygy_mycelium.database import Database
from syzygy_mycelium.peer_registry import (
    PeerRegistrationRequest,
    PeerRegistry,
    PeerRegistryError,
)


def build_registry() -> PeerRegistry:
    database = Database("sqlite:///:memory:")
    database.initialize()
    return PeerRegistry(database)


def test_peer_registry_registers_and_gets_peer() -> None:
    registry = build_registry()

    record = registry.register(
        PeerRegistrationRequest(
            node_id="desktop",
            name="Desktop",
            address="http://192.168.0.10:8030",
            capabilities=["sync", " health ", "sync"],
        )
    )

    assert record.node_id == "desktop"
    assert record.name == "Desktop"
    assert record.address == "http://192.168.0.10:8030"
    assert record.capabilities == ["sync", "health"]
    assert registry.get("desktop") == record


def test_peer_registry_lists_peers_by_name() -> None:
    registry = build_registry()

    registry.register(
        PeerRegistrationRequest(
            node_id="notebook",
            name="Notebook",
            address="http://192.168.0.11:8030",
        )
    )
    registry.register(
        PeerRegistrationRequest(
            node_id="desktop",
            name="Desktop",
            address="http://192.168.0.10:8030",
        )
    )

    assert [peer.name for peer in registry.list_peers()] == ["Desktop", "Notebook"]


def test_peer_registry_updates_existing_peer() -> None:
    registry = build_registry()

    original = registry.register(
        PeerRegistrationRequest(
            node_id="desktop",
            name="Desktop",
            address="http://192.168.0.10:8030",
            status="known",
        )
    )
    updated = registry.register(
        PeerRegistrationRequest(
            node_id="desktop",
            name="Desktop Office",
            address="http://192.168.0.12:8030",
            status="online",
        )
    )

    assert updated.created_at == original.created_at
    assert updated.updated_at >= original.updated_at
    assert updated.name == "Desktop Office"
    assert updated.status == "online"


def test_peer_registry_rejects_blank_values() -> None:
    registry = build_registry()

    try:
        registry.register(
            PeerRegistrationRequest(
                node_id="   ",
                name="Desktop",
                address="http://192.168.0.10:8030",
            )
        )
    except PeerRegistryError:
        return

    raise AssertionError("blank node_id should be rejected")
