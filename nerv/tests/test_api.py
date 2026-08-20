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
from syzygy_nerv.main import create_app
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


def build_client() -> TestClient:
    settings = Settings(register_with_foundation=False, foundation_registry_enabled=False)
    catalog = SurfaceCatalog(settings)
    supervisor = FakeSupervisor(catalog, settings.runtime_logs_dir)
    dashboard_service = FakeDashboardService(catalog, supervisor)
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
