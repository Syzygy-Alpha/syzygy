import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from syzygy_nerv.catalog import SurfaceCatalog
from syzygy_nerv.config import Settings, get_settings
from syzygy_nerv.dashboard_service import DashboardState, NervDashboardService
from syzygy_nerv.foundation_client import FoundationClient
from syzygy_nerv.module import ModuleDescriptor, nerv_descriptor
from syzygy_nerv.surface_actions import (
    SurfaceActionError,
    SurfaceActionExecutor,
    SurfaceActionResult,
)
from syzygy_nerv.supervisor import ModuleRuntimeStatus, ModuleSupervisor, ModuleSupervisorError

logger = logging.getLogger(__name__)


def create_app(
    settings: Settings | None = None,
    catalog: SurfaceCatalog | None = None,
    supervisor: ModuleSupervisor | None = None,
    dashboard_service: NervDashboardService | None = None,
    foundation_client: FoundationClient | None = None,
    action_executor: SurfaceActionExecutor | None = None,
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

    return app


app = create_app()
