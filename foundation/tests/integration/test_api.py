from fastapi.testclient import TestClient
from pydantic import SecretStr

from syzygy_foundation.config import Settings
from syzygy_foundation.main import create_app


def build_client() -> TestClient:
    settings = Settings(
        nats_enabled=False,
        database_url="sqlite:///:memory:",
        jwt_secret=SecretStr("test-secret-with-at-least-thirty-two-bytes"),
        admin_username="admin",
        admin_password=SecretStr("password"),
    )
    return TestClient(create_app(settings))


def auth_headers(client: TestClient) -> dict[str, str]:
    token_response = client.post(
        "/auth/token",
        json={"username": "admin", "password": "password"},
    )
    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_and_version_endpoints() -> None:
    with build_client() as client:
        health = client.get("/health")
        version = client.get("/version")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert version.status_code == 200
    assert version.json() == {"name": "syzygy-foundation", "version": "0.1.0"}


def test_auth_token_and_current_user() -> None:
    with build_client() as client:
        token_response = client.post(
            "/auth/token",
            json={"username": "admin", "password": "password"},
        )
        token = token_response.json()["access_token"]
        current_user = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert token_response.status_code == 200
    assert current_user.status_code == 200
    assert current_user.json() == {"username": "admin"}


def test_invalid_credentials_are_rejected() -> None:
    with build_client() as client:
        response = client.post(
            "/auth/token",
            json={"username": "admin", "password": "wrong"},
        )

    assert response.status_code == 401


def test_modules_endpoint_exposes_foundation_contract() -> None:
    with build_client() as client:
        response = client.get("/modules", headers=auth_headers(client))

    assert response.status_code == 200
    modules = response.json()
    assert modules[0]["name"] == "foundation"
    assert "event_bus" in modules[0]["capabilities"]


def test_modules_endpoint_requires_authentication() -> None:
    with build_client() as client:
        response = client.get("/modules")

    assert response.status_code == 401


def test_module_registration_and_lookup() -> None:
    with build_client() as client:
        headers = auth_headers(client)
        register = client.post(
            "/modules/register",
            headers=headers,
            json={
                "name": "forge",
                "version": "0.1.0",
                "status": "offline",
                "health": {"status": "unknown"},
                "capabilities": ["git", "build"],
                "dependencies": ["foundation"],
            },
        )
        lookup = client.get("/modules/forge", headers=headers)

    assert register.status_code == 200
    assert lookup.status_code == 200
    assert lookup.json()["capabilities"] == ["git", "build"]


def test_module_status_and_health_updates() -> None:
    with build_client() as client:
        headers = auth_headers(client)
        client.post(
            "/modules/register",
            headers=headers,
            json={
                "name": "observatory",
                "version": "0.1.0",
                "capabilities": ["logs"],
            },
        )
        status = client.patch(
            "/modules/observatory/status",
            headers=headers,
            json={"status": "stopped"},
        )
        health = client.patch(
            "/modules/observatory/health",
            headers=headers,
            json={"health": {"status": "error", "details": {"reason": "no collector"}}},
        )

    assert status.status_code == 200
    assert status.json()["status"] == "stopped"
    assert health.status_code == 200
    assert health.json()["status"] == "degraded"
    assert health.json()["health"]["details"] == {"reason": "no collector"}
