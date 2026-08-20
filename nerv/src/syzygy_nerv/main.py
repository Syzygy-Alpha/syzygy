import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from syzygy_nerv.catalog import SurfaceCatalog
from syzygy_nerv.config import Settings, get_settings
from syzygy_nerv.dashboard_service import DashboardState, NervDashboardService
from syzygy_nerv.forge_client import (
    ForgeClient,
    ForgeClientError,
    ForgeProjectCommandPlan,
    ForgeProjectCommandRunResult,
)
from syzygy_nerv.forge_workbench import ForgeWorkbenchService, ForgeWorkbenchSnapshot
from syzygy_nerv.foundation_client import FoundationClient
from syzygy_nerv.module import ModuleDescriptor, nerv_descriptor
from syzygy_nerv.supervisor import ModuleRuntimeStatus, ModuleSupervisor, ModuleSupervisorError
from syzygy_nerv.surface_actions import (
    SurfaceActionError,
    SurfaceActionExecutor,
    SurfaceActionResult,
)

logger = logging.getLogger(__name__)


def create_app(
    settings: Settings | None = None,
    catalog: SurfaceCatalog | None = None,
    supervisor: ModuleSupervisor | None = None,
    dashboard_service: NervDashboardService | None = None,
    foundation_client: FoundationClient | None = None,
    action_executor: SurfaceActionExecutor | None = None,
    forge_workbench_service: ForgeWorkbenchService | None = None,
) -> FastAPI:
    app_settings = settings or get_settings()
    logging.basicConfig(level=app_settings.log_level.upper())

    descriptor = nerv_descriptor(app_settings.version)
    catalog_instance = catalog or SurfaceCatalog(app_settings)
    foundation_client_instance = foundation_client or FoundationClient(
        base_url=app_settings.foundation_url,
        username=app_settings.foundation_username,
        password=app_settings.foundation_password.get_secret_value(),
    )
    supervisor_instance = supervisor or ModuleSupervisor(
        catalog=catalog_instance,
        runtime_logs_dir=app_settings.runtime_logs_dir,
    )
    dashboard_service_instance = dashboard_service or NervDashboardService(
        catalog=catalog_instance,
        supervisor=supervisor_instance,
        foundation_client=foundation_client_instance,
        foundation_registry_enabled=app_settings.foundation_registry_enabled,
        probe_timeout_seconds=app_settings.probe_timeout_seconds,
    )
    action_executor_instance = action_executor or SurfaceActionExecutor(
        catalog=catalog_instance,
        timeout_seconds=app_settings.probe_timeout_seconds,
    )
    forge_entry = catalog_instance.get("forge")
    if forge_entry is None:
        raise ValueError("NERV requires a Forge surface in its catalog")
    forge_workbench_service_instance = forge_workbench_service or ForgeWorkbenchService(
        ForgeClient(
            base_url=forge_entry.links.root_url,
            timeout_seconds=app_settings.probe_timeout_seconds,
        )
    )
    static_dir = Path(__file__).resolve().parent / "static"
    html_path = static_dir / "index.html"

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if app_settings.register_with_foundation:
            try:
                await foundation_client_instance.register_module(descriptor)
                logger.info("nerv_registered_with_foundation")
            except Exception:
                logger.exception("nerv_registration_failed")
        try:
            yield
        finally:
            supervisor_instance.shutdown()

    app = FastAPI(title="SYZYGY NERV", version=app_settings.version, lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.state.settings = app_settings
    app.state.descriptor = descriptor
    app.state.catalog = catalog_instance
    app.state.foundation_client = foundation_client_instance
    app.state.supervisor = supervisor_instance
    app.state.dashboard_service = dashboard_service_instance
    app.state.action_executor = action_executor_instance
    app.state.forge_workbench_service = forge_workbench_service_instance

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> str:
        return html_path.read_text(encoding="utf-8")

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "checks": {"module": "ok", "dashboard": "ok"}}

    @app.get("/version")
    def version() -> dict[str, str]:
        return {"name": app_settings.service_name, "version": app_settings.version}

    @app.get("/capabilities")
    def capabilities() -> ModuleDescriptor:
        return descriptor

    @app.get("/api/dashboard")
    async def api_dashboard() -> DashboardState:
        return await dashboard_service_instance.dashboard_state()

    @app.post("/api/surfaces/{name}/start")
    def start_surface(name: str) -> ModuleRuntimeStatus:
        try:
            return supervisor_instance.start(name)
        except ModuleSupervisorError as exc:
            detail = str(exc)
            code = (
                status.HTTP_404_NOT_FOUND
                if detail.startswith("Unknown")
                else status.HTTP_400_BAD_REQUEST
            )
            raise HTTPException(status_code=code, detail=detail) from exc

    @app.post("/api/surfaces/{name}/stop")
    def stop_surface(name: str) -> ModuleRuntimeStatus:
        try:
            return supervisor_instance.stop(name)
        except ModuleSupervisorError as exc:
            detail = str(exc)
            code = (
                status.HTTP_404_NOT_FOUND
                if detail.startswith("Unknown")
                else status.HTTP_400_BAD_REQUEST
            )
            raise HTTPException(status_code=code, detail=detail) from exc

    @app.post("/api/surfaces/{name}/actions/{action_name}/run")
    async def run_surface_action(name: str, action_name: str) -> SurfaceActionResult:
        try:
            return await action_executor_instance.execute(name, action_name)
        except SurfaceActionError as exc:
            detail = str(exc)
            code = (
                status.HTTP_404_NOT_FOUND
                if detail.startswith("Unknown")
                else status.HTTP_400_BAD_REQUEST
            )
            raise HTTPException(status_code=code, detail=detail) from exc

    @app.get("/api/forge/projects")
    async def forge_projects() -> ForgeWorkbenchSnapshot:
        return await forge_workbench_service_instance.snapshot()

    @app.get("/api/forge/commands/plan")
    async def forge_command_plan(project: str, command: str) -> ForgeProjectCommandPlan:
        try:
            return await forge_workbench_service_instance.forge_client.command_plan(
                project,
                command,
            )
        except ForgeClientError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post("/api/forge/commands/run")
    async def run_forge_command(
        project: str,
        command: str,
        confirm: bool = False,
        timeout_seconds: int = Query(default=30, ge=1, le=120),
    ) -> ForgeProjectCommandRunResult:
        if not confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NERV command execution requires confirm=true",
            )
        try:
            return await forge_workbench_service_instance.forge_client.run_command(
                project,
                command,
                timeout_seconds,
            )
        except ForgeClientError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return app


app = create_app()
