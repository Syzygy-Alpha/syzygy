import asyncio
from datetime import UTC, datetime

import httpx
from pydantic import BaseModel, Field

from syzygy_nerv.catalog import SurfaceAction, SurfaceCatalog, SurfaceEntry, SurfaceLinks
from syzygy_nerv.foundation_client import FoundationClient, FoundationModuleDescriptor
from syzygy_nerv.supervisor import ModuleRuntimeStatus, ModuleSupervisor


class SurfaceProbe(BaseModel):
    reachable: bool
    http_status: int | None = None
    service_status: str | None = None
    error: str | None = None


class FoundationRegistrySnapshot(BaseModel):
    enabled: bool
    reachable: bool
    module_count: int = 0
    checked_at: datetime | None = None
    error: str | None = None
    modules: list[FoundationModuleDescriptor] = Field(default_factory=list)


class DashboardSurface(BaseModel):
    name: str
    label: str
    group: str
    description: str
    accent: str
    cwd: str
    launch_command: list[str] = Field(default_factory=list)
    launch_enabled: bool
    links: SurfaceLinks
    actions: list[SurfaceAction] = Field(default_factory=list)
    runtime: ModuleRuntimeStatus
    probe: SurfaceProbe
    foundation_status: str | None = None
    foundation_health: str | None = None
    foundation_version: str | None = None


class DashboardSummary(BaseModel):
    known_surfaces: int
    launchable_surfaces: int
    running_surfaces: int
    reachable_surfaces: int


class DashboardState(BaseModel):
    generated_at: datetime
    foundation_registry: FoundationRegistrySnapshot
    summary: DashboardSummary
    surfaces: list[DashboardSurface] = Field(default_factory=list)


class NervDashboardService:
    def __init__(
        self,
        catalog: SurfaceCatalog,
        supervisor: ModuleSupervisor,
        foundation_client: FoundationClient,
        foundation_registry_enabled: bool,
        probe_timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.catalog = catalog
        self.supervisor = supervisor
        self.foundation_client = foundation_client
        self.foundation_registry_enabled = foundation_registry_enabled
        self.probe_timeout_seconds = probe_timeout_seconds
        self.transport = transport

    async def dashboard_state(self) -> DashboardState:
        foundation_registry = await self._foundation_registry()
        registry_by_name = {module.name: module for module in foundation_registry.modules}
        runtime_snapshot = self.supervisor.snapshot()
        entries = self.catalog.list_entries()
        probes = await asyncio.gather(*(self._probe(entry) for entry in entries))

        surfaces = [
            self._surface(
                entry,
                runtime_snapshot[entry.name],
                probe,
                registry_by_name.get(entry.name),
            )
            for entry, probe in zip(entries, probes, strict=True)
        ]
        summary = DashboardSummary(
            known_surfaces=len(surfaces),
            launchable_surfaces=sum(1 for surface in surfaces if surface.launch_enabled),
            running_surfaces=sum(1 for surface in surfaces if surface.runtime.running),
            reachable_surfaces=sum(1 for surface in surfaces if surface.probe.reachable),
        )
        return DashboardState(
            generated_at=datetime.now(UTC),
            foundation_registry=foundation_registry,
            summary=summary,
            surfaces=surfaces,
        )

    async def _foundation_registry(self) -> FoundationRegistrySnapshot:
        if not self.foundation_registry_enabled:
            return FoundationRegistrySnapshot(enabled=False, reachable=False)
        try:
            modules = await self.foundation_client.list_modules()
        except Exception as exc:
            return FoundationRegistrySnapshot(
                enabled=True,
                reachable=False,
                checked_at=datetime.now(UTC),
                error=str(exc),
            )
        return FoundationRegistrySnapshot(
            enabled=True,
            reachable=True,
            module_count=len(modules),
            checked_at=datetime.now(UTC),
            modules=modules,
        )

    async def _probe(self, entry: SurfaceEntry) -> SurfaceProbe:
        try:
            async with httpx.AsyncClient(
                timeout=self.probe_timeout_seconds,
                transport=self.transport,
            ) as client:
                response = await client.get(entry.links.health_url)
        except Exception as exc:
            return SurfaceProbe(reachable=False, error=str(exc))
        content_type = response.headers.get("content-type", "")
        payload = response.json() if content_type.startswith("application/json") else {}
        service_status = payload.get("status") if isinstance(payload, dict) else None
        return SurfaceProbe(
            reachable=response.status_code == 200,
            http_status=response.status_code,
            service_status=service_status if isinstance(service_status, str) else None,
        )

    def _surface(
        self,
        entry: SurfaceEntry,
        runtime: ModuleRuntimeStatus,
        probe: SurfaceProbe,
        foundation_module: FoundationModuleDescriptor | None,
    ) -> DashboardSurface:
        return DashboardSurface(
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
            runtime=runtime,
            probe=probe,
            foundation_status=foundation_module.status if foundation_module is not None else None,
            foundation_health=(
                foundation_module.health.status if foundation_module is not None else None
            ),
            foundation_version=foundation_module.version if foundation_module is not None else None,
        )
