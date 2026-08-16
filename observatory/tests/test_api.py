from fastapi.testclient import TestClient

from syzygy_observatory.config import Settings
from syzygy_observatory.main import create_app


def build_client(database_url: str = "sqlite:///:memory:") -> TestClient:
    settings = Settings(register_with_foundation=False, database_url=database_url)
    return TestClient(create_app(settings))


def test_health_version_and_capabilities() -> None:
    with build_client() as client:
        health = client.get("/health")
        version = client.get("/version")
        capabilities = client.get("/capabilities")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert version.status_code == 200
    assert version.json() == {"name": "syzygy-observatory", "version": "0.1.0"}
    assert capabilities.status_code == 200
    assert capabilities.json()["name"] == "observatory"
    assert "health_summary" in capabilities.json()["capabilities"]


def test_health_observation_endpoints_record_list_and_summarize() -> None:
    with build_client() as client:
        created = client.post(
            "/health-observations",
            json={
                "name": "forge",
                "status": "ok",
                "source": "manual",
                "details": {"url": "http://127.0.0.1:8010/health"},
            },
        )
        listed = client.get("/health-observations")
        filtered = client.get("/health-observations?status=ok")
        summary = client.get("/health-observations/summary")

    assert created.status_code == 201
    assert created.json()["name"] == "forge"
    assert listed.status_code == 200
    assert [record["name"] for record in listed.json()] == ["forge"]
    assert filtered.status_code == 200
    assert [record["status"] for record in filtered.json()] == ["ok"]
    assert summary.status_code == 200
    assert summary.json()["total"] == 1
    assert summary.json()["by_status"] == {"ok": 1}
    assert summary.json()["latest_by_name"][0]["name"] == "forge"


def test_health_observation_trends_endpoint() -> None:
    with build_client() as client:
        client.post("/health-observations", json={"name": "forge", "status": "ok"})
        client.post("/health-observations", json={"name": "forge", "status": "degraded"})
        response = client.get("/health-observations/trends?name=forge")

    assert response.status_code == 200
    assert response.json()["total_services"] == 1
    assert response.json()["trends"][0]["name"] == "forge"
    assert response.json()["trends"][0]["latest_status"] == "degraded"
    assert response.json()["trends"][0]["status_changes"] == 1


def test_foundation_module_ingest_endpoint_requires_confirmation() -> None:
    with build_client() as client:
        response = client.post("/ingest/foundation/modules", json={"confirm": False})

    assert response.status_code == 400
    assert response.json()["detail"] == "Foundation module ingestion requires confirm=true"


def test_foundation_module_polling_status_endpoint() -> None:
    with build_client() as client:
        response = client.get("/ingest/foundation/modules/polling")

    assert response.status_code == 200
    assert response.json() == {
        "enabled": False,
        "running": False,
        "interval_seconds": 60,
        "last_observed": None,
        "last_error": None,
    }
