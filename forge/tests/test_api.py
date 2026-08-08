from pathlib import Path

from fastapi.testclient import TestClient

from syzygy_forge.config import Settings
from syzygy_forge.main import create_app


def build_client(
    workspace_root: Path | None = None,
    database_url: str = "sqlite:///:memory:",
) -> TestClient:
    settings = Settings(
        register_with_foundation=False,
        database_url=database_url,
        workspace_root=workspace_root or Path("."),
    )
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
    assert "project_creation" in payload["capabilities"]


def test_current_project_endpoint_reports_configured_workspace(tmp_path: Path) -> None:
    with build_client(workspace_root=tmp_path) as client:
        response = client.get("/projects/current")

    assert response.status_code == 200
    payload = response.json()
    assert payload["path"] == str(tmp_path.resolve())
    assert payload["exists"] is True


def test_project_registry_endpoints_register_list_and_get(tmp_path: Path) -> None:
    with build_client() as client:
        created = client.post(
            "/projects",
            json={"name": "syzygy", "path": str(tmp_path)},
        )
        listed = client.get("/projects")
        fetched = client.get("/projects/syzygy")

    assert created.status_code == 201
    assert created.json()["path"] == str(tmp_path.resolve())
    assert listed.status_code == 200
    assert [project["name"] for project in listed.json()] == ["syzygy"]
    assert fetched.status_code == 200
    assert fetched.json()["record"]["name"] == "syzygy"
    assert fetched.json()["inspection"]["exists"] is True


def test_project_registry_endpoint_rejects_missing_path(tmp_path: Path) -> None:
    with build_client() as client:
        response = client.post(
            "/projects",
            json={"name": "missing", "path": str(tmp_path / "missing")},
        )

    assert response.status_code == 400


def test_project_template_endpoints() -> None:
    with build_client() as client:
        listed = client.get("/project-templates")
        fetched = client.get("/project-templates/python-cli")

    assert listed.status_code == 200
    assert [template["name"] for template in listed.json()] == ["python-cli"]
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "python-cli"


def test_create_project_endpoint_creates_and_registers_project(tmp_path: Path) -> None:
    with build_client(workspace_root=tmp_path) as client:
        created = client.post(
            "/projects/create",
            json={"name": "hello-tool", "template": "python-cli"},
        )
        listed = client.get("/projects")
        commands = client.get("/projects/hello-tool/commands")

    assert created.status_code == 201
    payload = created.json()
    assert payload["record"]["name"] == "hello-tool"
    assert payload["template"] == "python-cli"
    assert payload["git_initialized"] is False
    assert "src/hello_tool/main.py" in payload["files"]
    assert (tmp_path / "hello-tool" / "syzygy.project.toml").exists()
    assert listed.status_code == 200
    assert [project["name"] for project in listed.json()] == ["hello-tool"]
    assert commands.status_code == 200
    assert [command["name"] for command in commands.json()["commands"]] == ["lint", "run", "test"]


def test_create_project_endpoint_rejects_invalid_name(tmp_path: Path) -> None:
    with build_client(workspace_root=tmp_path) as client:
        response = client.post(
            "/projects/create",
            json={"name": "../outside", "template": "python-cli"},
        )

    assert response.status_code == 400


def test_project_commands_endpoint_rejects_project_without_manifest(tmp_path: Path) -> None:
    with build_client() as client:
        client.post("/projects", json={"name": "plain", "path": str(tmp_path)})
        response = client.get("/projects/plain/commands")

    assert response.status_code == 400
