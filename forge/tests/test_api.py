from pathlib import Path
from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

from syzygy_forge.config import Settings
from syzygy_forge.main import create_app


def build_client(
    workspace_root: Path | None = None,
    database_url: str = "sqlite:///:memory:",
    event_publisher_enabled: bool = False,
) -> TestClient:
    settings = Settings(
        register_with_foundation=False,
        database_url=database_url,
        event_publisher_enabled=event_publisher_enabled,
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
    assert "event_outbox" in payload["capabilities"]
    assert "event_outbox_publishing" in payload["capabilities"]
    assert "event_outbox_requeue" in payload["capabilities"]
    assert "event_outbox_summary" in payload["capabilities"]
    assert "project_command_execution" in payload["capabilities"]
    assert "project_creation" in payload["capabilities"]
    assert "project_command_planning" in payload["capabilities"]


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
    assert [template["name"] for template in listed.json()] == [
        "python-cli",
        "python-package",
        "static-site",
    ]
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
        plan = client.get("/projects/hello-tool/commands/test/plan")

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
    assert plan.status_code == 200
    assert plan.json()["allowed"] is True
    assert plan.json()["argv"] == ["python", "-m", "pytest"]


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


def test_project_command_run_endpoint_requires_confirmation(tmp_path: Path) -> None:
    (tmp_path / "syzygy.project.toml").write_text(
        """
name = "plain"

[commands]
hello = 'python -c "print(123)"'
""",
        encoding="utf-8",
    )
    with build_client() as client:
        client.post("/projects", json={"name": "plain", "path": str(tmp_path)})
        response = client.post(
            "/projects/plain/commands/hello/runs",
            json={"confirm": False, "timeout_seconds": 5},
        )

    assert response.status_code == 400


def test_project_command_run_endpoint_executes_confirmed_allowed_command(tmp_path: Path) -> None:
    (tmp_path / "syzygy.project.toml").write_text(
        """
name = "plain"

[commands]
hello = 'python -c "print(123)"'
""",
        encoding="utf-8",
    )
    with build_client() as client:
        client.post("/projects", json={"name": "plain", "path": str(tmp_path)})
        response = client.post(
            "/projects/plain/commands/hello/runs",
            json={"confirm": True, "timeout_seconds": 5},
        )
        history = client.get("/projects/plain/command-runs")
        outbox = client.get("/events/outbox")

    assert response.status_code == 201
    payload = response.json()
    assert payload["run_id"] == 1
    assert payload["returncode"] == 0
    assert payload["stdout"].strip() == "123"
    assert payload["timed_out"] is False
    assert history.status_code == 200
    history_payload = history.json()
    assert len(history_payload) == 1
    assert history_payload[0]["id"] == 1
    assert history_payload[0]["project"] == "plain"
    assert history_payload[0]["command_name"] == "hello"
    assert outbox.status_code == 200
    outbox_payload = outbox.json()
    assert [event["name"] for event in outbox_payload] == [
        "CommandRunStarted",
        "CommandRunCompleted",
    ]
    assert "stdout" not in outbox_payload[1]["payload"]
    assert "stderr" not in outbox_payload[1]["payload"]


def test_event_outbox_publish_endpoint_is_disabled_by_default() -> None:
    with build_client() as client:
        response = client.post("/events/outbox/publish", json={"confirm": True})

    assert response.status_code == 400
    assert response.json()["detail"] == "Event publisher is disabled"


def test_event_outbox_summary_endpoint_reports_empty_state() -> None:
    with build_client() as client:
        response = client.get("/events/outbox/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total": 0,
        "pending": 0,
        "published": 0,
        "failed": 0,
        "by_status": {},
        "total_attempts": 0,
        "max_attempts": 0,
        "delivery_status": "ok",
        "oldest_pending": None,
        "latest_failed": None,
    }


def test_event_outbox_summary_endpoint_reports_delivery_state(tmp_path: Path) -> None:
    (tmp_path / "syzygy.project.toml").write_text(
        """
name = "plain"

[commands]
hello = 'python -c "print(123)"'
""",
        encoding="utf-8",
    )
    with build_client() as client:
        client.post("/projects", json={"name": "plain", "path": str(tmp_path)})
        client.post(
            "/projects/plain/commands/hello/runs",
            json={"confirm": True, "timeout_seconds": 5},
        )
        cast(FastAPI, client.app).state.event_outbox.mark_failed(2, "transport unavailable")
        response = client.get("/events/outbox/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert payload["pending"] == 1
    assert payload["published"] == 0
    assert payload["failed"] == 1
    assert payload["by_status"] == {"failed": 1, "pending": 1}
    assert payload["total_attempts"] == 1
    assert payload["max_attempts"] == 1
    assert payload["delivery_status"] == "attention"
    assert payload["oldest_pending"]["id"] == 1
    assert payload["latest_failed"]["id"] == 2


def test_event_outbox_publish_endpoint_publishes_pending_events(tmp_path: Path) -> None:
    (tmp_path / "syzygy.project.toml").write_text(
        """
name = "plain"

[commands]
hello = 'python -c "print(123)"'
""",
        encoding="utf-8",
    )
    with build_client(event_publisher_enabled=True) as client:
        client.post("/projects", json={"name": "plain", "path": str(tmp_path)})
        client.post(
            "/projects/plain/commands/hello/runs",
            json={"confirm": True, "timeout_seconds": 5},
        )
        response = client.post("/events/outbox/publish", json={"confirm": True})
        outbox = client.get("/events/outbox")

    assert response.status_code == 200
    assert response.json() == {
        "attempted": 2,
        "published": 2,
        "failed": 0,
        "failures": [],
    }
    assert [event["status"] for event in outbox.json()] == ["published", "published"]
    assert [event["attempts"] for event in outbox.json()] == [1, 1]


def test_event_outbox_requeue_endpoint_requires_confirmation() -> None:
    with build_client() as client:
        response = client.post("/events/outbox/1/requeue", json={"confirm": False})

    assert response.status_code == 400
    assert response.json()["detail"] == "Event requeue requires confirm=true"


def test_event_outbox_requeue_endpoint_requeues_failed_event(tmp_path: Path) -> None:
    (tmp_path / "syzygy.project.toml").write_text(
        """
name = "plain"

[commands]
hello = 'python -c "print(123)"'
""",
        encoding="utf-8",
    )
    with build_client() as client:
        client.post("/projects", json={"name": "plain", "path": str(tmp_path)})
        client.post(
            "/projects/plain/commands/hello/runs",
            json={"confirm": True, "timeout_seconds": 5},
        )
        cast(FastAPI, client.app).state.event_outbox.mark_failed(1, "transport unavailable")
        response = client.post("/events/outbox/1/requeue", json={"confirm": True})
        outbox = client.get("/events/outbox")

    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    assert response.json()["attempts"] == 1
    assert response.json()["last_error"] is None
    assert [event["status"] for event in outbox.json()] == ["pending", "pending"]


def test_event_outbox_requeue_endpoint_rejects_non_failed_event(tmp_path: Path) -> None:
    (tmp_path / "syzygy.project.toml").write_text(
        """
name = "plain"

[commands]
hello = 'python -c "print(123)"'
""",
        encoding="utf-8",
    )
    with build_client() as client:
        client.post("/projects", json={"name": "plain", "path": str(tmp_path)})
        client.post(
            "/projects/plain/commands/hello/runs",
            json={"confirm": True, "timeout_seconds": 5},
        )
        response = client.post("/events/outbox/1/requeue", json={"confirm": True})

    assert response.status_code == 400
    assert "Only failed event outbox records can be requeued" in response.json()["detail"]


def test_event_outbox_requeue_endpoint_reports_missing_event() -> None:
    with build_client() as client:
        response = client.post("/events/outbox/404/requeue", json={"confirm": True})

    assert response.status_code == 404
    assert "404" in response.json()["detail"]


def test_event_outbox_requeue_failed_endpoint_requeues_failed_events(tmp_path: Path) -> None:
    (tmp_path / "syzygy.project.toml").write_text(
        """
name = "plain"

[commands]
hello = 'python -c "print(123)"'
""",
        encoding="utf-8",
    )
    with build_client() as client:
        client.post("/projects", json={"name": "plain", "path": str(tmp_path)})
        client.post(
            "/projects/plain/commands/hello/runs",
            json={"confirm": True, "timeout_seconds": 5},
        )
        cast(FastAPI, client.app).state.event_outbox.mark_failed(1, "transport unavailable")
        response = client.post(
            "/events/outbox/requeue-failed",
            json={"confirm": True, "limit": 10},
        )
        outbox = client.get("/events/outbox")

    assert response.status_code == 200
    assert response.json()["requeued"] == 1
    assert [event["id"] for event in response.json()["events"]] == [1]
    assert [event["status"] for event in outbox.json()] == ["pending", "pending"]
