from fastapi.testclient import TestClient

from syzygy_forge.config import Settings
from syzygy_forge.main import create_app


def build_client() -> TestClient:
    settings = Settings(register_with_foundation=False)
    return TestClient(create_app(settings))


def test_health_and_version() -> None:
    with build_client() as client:
        health = client.get("/health")
        version = client.get("/version")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert version.status_code == 200
    assert version.json() == {"name": "syzygy-forge", "version": "0.1.0"}


def test_capabilities_expose_forge_descriptor() -> None:
    with build_client() as client:
        response = client.get("/capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "forge"
    assert payload["dependencies"] == ["foundation"]
    assert "git" in payload["capabilities"]

