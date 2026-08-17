from fastapi.testclient import TestClient

from syzygy_mycelium.config import Settings
from syzygy_mycelium.main import create_app


def build_client() -> TestClient:
    settings = Settings(register_with_foundation=False)
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
    assert version.status_code == 200
    assert version.json() == {"name": "syzygy-mycelium", "version": "0.1.0"}
    assert capabilities.status_code == 200
    assert capabilities.json()["name"] == "mycelium"
    assert "local_node_descriptor" in capabilities.json()["capabilities"]
    assert node.status_code == 200
    assert node.json()["agent"] == "hypha"
    assert node.json()["node_id"] == "local-node"
