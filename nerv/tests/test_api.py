from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from syzygy_nerv.catalog import SurfaceCatalog
from syzygy_nerv.config import Settings
from syzygy_nerv.dashboard_service import (
    DashboardState,
    DashboardSummary,
    DashboardSurface,
    FoundationRegistrySnapshot,
    NervDashboardService,
    SurfaceProbe,
)
from syzygy_nerv.foundation_client import FoundationClient
from syzygy_nerv.forge_client import (
    ForgeClient,
    ForgeProject,
    ForgeProjectCommand,
    ForgeProjectCommandPlan,
    ForgeProjectCommandRunResult,
    ForgeProjectCommandSet,
)
from syzygy_nerv.forge_workbench import ForgeWorkbenchService
from syzygy_nerv.main import create_app
from syzygy_nerv.surface_actions import SurfaceActionExecutor, SurfaceActionResult
from syzygy_nerv.supervisor import ModuleRuntimeStatus, ModuleSupervisor


class FakeDashboardService(NervDashboardService):
    def __init__(self, catalog: SurfaceCatalog, supervisor: ModuleSupervisor) -> None:
        self.catalog = catalog
        self.supervisor = supervisor

    async def dashboard_state(self) -> DashboardState:  # type: ignore[override]
        entry = self.catalog.get("foundation")
        assert entry is not None
        return DashboardState(
            generated_at=datetime.now(UTC),
            foundation_registry=FoundationRegistrySnapshot(enabled=False, reachable=False),
            summary=DashboardSummary(
                known_surfaces=1,
                launchable_surfaces=1,
                running_surfaces=0,
                reachable_surfaces=0,
            ),
            surfaces=[
                DashboardSurface(
                    name=entry.name,
                    label=entry.label,
                    group=entry.group,
                    description=entry.description,
                    accent=entry.accent,
                    cwd=entry.cwd,
                    launch_command=entry.launch_command,
                    launch_enabled=entry.launch_enabled,
                    links=entry.links,
                    actions=entry.actions,
                    runtime=ModuleRuntimeStatus(name=entry.name, running=False, cwd=entry.cwd),
                    probe=SurfaceProbe(reachable=False, error="offline"),
                )
            ],
        )


class FakeSupervisor(ModuleSupervisor):
    def __init__(self, catalog: SurfaceCatalog, runtime_logs_dir: Path) -> None:
        super().__init__(catalog, runtime_logs_dir)
        self.started: list[str] = []
        self.stopped: list[str] = []

    def start(self, name: str) -> ModuleRuntimeStatus:  # type: ignore[override]
        self.started.append(name)
        entry = self.catalog.get(name)
        assert entry is not None
        return ModuleRuntimeStatus(name=name, running=True, cwd=entry.cwd, pid=1000)

    def stop(self, name: str) -> ModuleRuntimeStatus:  # type: ignore[override]
        self.stopped.append(name)
        entry = self.catalog.get(name)
        assert entry is not None
        return ModuleRuntimeStatus(name=name, running=False, cwd=entry.cwd)

    def shutdown(self) -> None:  # type: ignore[override]
        return


class FakeActionExecutor(SurfaceActionExecutor):
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    async def execute(
        self,
        surface_name: str,
        action_name: str,
    ) -> SurfaceActionResult:  # type: ignore[override]
        self.calls.append((surface_name, action_name))
        return SurfaceActionResult(
            surface=surface_name,
            action=action_name,
            label="Current Project",
            method="GET",
            url="http://127.0.0.1:8010/projects/current",
            ok=True,
            status_code=200,
            content_type="application/json",
            received_at=datetime.now(UTC),
            payload={"path": "C:/syzygy"},
        )


class FakeForgeClient(ForgeClient):
    def __init__(self) -> None:
        self.run_calls: list[tuple[str, str, int]] = []
        self.project = ForgeProject(
            name="demo",
            path="C:/demo",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def list_projects(self) -> list[ForgeProject]:
        return [self.project]

    async def project_commands(self, project_name: str) -> ForgeProjectCommandSet:
        return ForgeProjectCommandSet(
            project=project_name,
            manifest_path="C:/demo/syzygy.project.toml",
            commands=[ForgeProjectCommand(name="test", command="python -m pytest")],
        )

    async def command_plan(
        self,
        project_name: str,
        command_name: str,
    ) -> ForgeProjectCommandPlan:
        return ForgeProjectCommandPlan(
            project=project_name,
            command_name=command_name,
            command="python -m pytest",
            cwd="C:/demo",
            argv=["python", "-m", "pytest"],
            allowed=True,
            reason="allowed",
        )

    async def run_command(
        self,
        project_name: str,
        command_name: str,
        timeout_seconds: int,
    ) -> ForgeProjectCommandRunResult:
        self.run_calls.append((project_name, command_name, timeout_seconds))
        now = datetime.now(UTC)
        return ForgeProjectCommandRunResult(
            run_id=1,
            plan=await self.command_plan(project_name, command_name),
            returncode=0,
            stdout="passed",
            started_at=now,
            completed_at=now,
        )


def build_client() -> TestClient:
    settings = Settings(register_with_foundation=False, foundation_registry_enabled=False)
    catalog = SurfaceCatalog(settings)
    supervisor = FakeSupervisor(catalog, settings.runtime_logs_dir)
    dashboard_service = FakeDashboardService(catalog, supervisor)
    action_executor = FakeActionExecutor()
    forge_workbench_service = ForgeWorkbenchService(FakeForgeClient())
    foundation_client = FoundationClient(
        base_url="http://foundation.test",
        username="admin",
        password="secret",
    )
    return TestClient(
        create_app(
            settings=settings,
            catalog=catalog,
            supervisor=supervisor,
            dashboard_service=dashboard_service,
            foundation_client=foundation_client,
            action_executor=action_executor,
            forge_workbench_service=forge_workbench_service,
        )
    )


def test_dashboard_root_and_api() -> None:
    with build_client() as client:
        root = client.get("/")
        health = client.get("/health")
        dashboard = client.get("/api/dashboard")

    assert root.status_code == 200
    assert "NERV COMMAND CENTER" in root.text
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert dashboard.status_code == 200
    assert dashboard.json()["summary"]["known_surfaces"] == 1


def test_surface_actions_delegate_to_supervisor() -> None:
    with build_client() as client:
        started = client.post("/api/surfaces/foundation/start")
        stopped = client.post("/api/surfaces/foundation/stop")

    assert started.status_code == 200
    assert started.json()["running"] is True
    assert stopped.status_code == 200
    assert stopped.json()["running"] is False


def test_surface_quick_action_endpoint_returns_payload() -> None:
    with build_client() as client:
        response = client.post("/api/surfaces/forge/actions/current-project/run")

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["payload"] == {"path": "C:/syzygy"}


def test_forge_workbench_exposes_projects_plans_and_confirmed_runs() -> None:
    with build_client() as client:
        projects = client.get("/api/forge/projects")
        plan = client.get(
            "/api/forge/commands/plan",
            params={"project": "demo", "command": "test"},
        )
        rejected_run = client.post(
            "/api/forge/commands/run",
            params={"project": "demo", "command": "test"},
        )
        confirmed_run = client.post(
            "/api/forge/commands/run",
            params={"project": "demo", "command": "test", "confirm": "true"},
        )

    assert projects.status_code == 200
    assert projects.json()["projects"][0]["project"]["name"] == "demo"
    assert plan.status_code == 200
    assert plan.json()["allowed"] is True
    assert rejected_run.status_code == 400
    assert confirmed_run.status_code == 200
    assert confirmed_run.json()["returncode"] == 0
