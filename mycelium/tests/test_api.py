from fastapi.testclient import TestClient

from syzygy_mycelium.config import Settings
from syzygy_mycelium.main import create_app


def build_client() -> TestClient:
    settings = Settings(register_with_foundation=False, database_url="sqlite:///:memory:")
    return TestClient(create_app(settings))


def test_health_version_capabilities_and_node() -> None:
    with build_client() as client:
        health = client.get("/health")
        version = client.get("/version")
        capabilities = client.get("/capabilities")
        node = client.get("/node")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["checks"]["node"] == "online"
    assert health.json()["checks"]["peer_registry"] == "ok"
    assert version.status_code == 200
    assert version.json() == {"name": "syzygy-mycelium", "version": "0.1.0"}
    assert capabilities.status_code == 200
    assert capabilities.json()["name"] == "mycelium"
    assert "local_node_descriptor" in capabilities.json()["capabilities"]
    assert "local_peer_registry" in capabilities.json()["capabilities"]
    assert node.status_code == 200
    assert node.json()["agent"] == "hypha"
    assert node.json()["node_id"] == "local-node"


def test_peer_registry_endpoints_register_list_and_get() -> None:
    with build_client() as client:
        created = client.post(
            "/peers",
            json={
                "node_id": "desktop",
                "name": "Desktop",
                "address": "http://192.168.0.10:8030",
                "capabilities": ["sync"],
            },
        )
        listed = client.get("/peers")
        loaded = client.get("/peers/desktop")

    assert created.status_code == 200
    assert created.json()["node_id"] == "desktop"
    assert created.json()["status"] == "known"
    assert listed.status_code == 200
    assert [peer["node_id"] for peer in listed.json()] == ["desktop"]
    assert loaded.status_code == 200
    assert loaded.json()["address"] == "http://192.168.0.10:8030"
