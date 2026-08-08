from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status

from syzygy_foundation.api.dependencies import current_user
from syzygy_foundation.auth.security import (
    AuthenticatedUser,
    TokenRequest,
    TokenResponse,
    authenticate_user,
    create_access_token,
)
from syzygy_foundation.events import EventName, FoundationEvent
from syzygy_foundation.events.bus import EventBus
from syzygy_foundation.health import HealthService
from syzygy_foundation.modules import (
    ModuleDescriptor,
    ModuleHealthUpdate,
    ModuleRegistration,
    ModuleRegistry,
    ModuleStatus,
    ModuleStatusUpdate,
)


def create_router() -> APIRouter:
    router = APIRouter()

    @router.get("/")
    def root(request: Request) -> dict[str, str]:
        settings = request.app.state.settings
        return {"name": settings.service_name, "status": "ok"}

    @router.get("/health")
    def health(request: Request) -> dict[str, Any]:
        health_service = HealthService(request.app.state.database, request.app.state.event_bus)
        return health_service.check()

    @router.get("/version")
    def version(request: Request) -> dict[str, str]:
        settings = request.app.state.settings
        return {"name": settings.service_name, "version": settings.version}

    @router.post("/auth/token")
    def token(request: Request, credentials: TokenRequest) -> TokenResponse:
        settings = request.app.state.settings
        if not authenticate_user(credentials.username, credentials.password, settings):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid credentials",
            )
        return TokenResponse(access_token=create_access_token(credentials.username, settings))

    @router.get("/auth/me")
    def me(user: Annotated[AuthenticatedUser, Depends(current_user)]) -> AuthenticatedUser:
        return user

    @router.post("/modules/register")
    async def register_module(
        request: Request,
        registration: ModuleRegistration,
        user: Annotated[AuthenticatedUser, Depends(current_user)],
    ) -> ModuleDescriptor:
        registry = cast(ModuleRegistry, request.app.state.module_registry)
        descriptor = ModuleDescriptor(**registration.model_dump())
        registry.register(descriptor)
        await publish_module_event(request, descriptor, event_for_status(descriptor.status))
        return descriptor

    @router.get("/modules")
    def modules(
        request: Request,
        user: Annotated[AuthenticatedUser, Depends(current_user)],
    ) -> list[ModuleDescriptor]:
        registry = request.app.state.module_registry
        return cast(ModuleRegistry, registry).list_modules()

    @router.get("/modules/{name}")
    def module(
        request: Request,
        name: str,
        user: Annotated[AuthenticatedUser, Depends(current_user)],
    ) -> ModuleDescriptor:
        registry = cast(ModuleRegistry, request.app.state.module_registry)
        descriptor = registry.get(name)
        if descriptor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="module not found")
        return descriptor

    @router.patch("/modules/{name}/status")
    async def update_module_status(
        request: Request,
        name: str,
        payload: ModuleStatusUpdate,
        user: Annotated[AuthenticatedUser, Depends(current_user)],
    ) -> ModuleDescriptor:
        registry = cast(ModuleRegistry, request.app.state.module_registry)
        descriptor = registry.update_status(name, payload.status)
        if descriptor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="module not found")
        await publish_module_event(request, descriptor, event_for_status(descriptor.status))
        return descriptor

    @router.patch("/modules/{name}/health")
    async def update_module_health(
        request: Request,
        name: str,
        payload: ModuleHealthUpdate,
        user: Annotated[AuthenticatedUser, Depends(current_user)],
    ) -> ModuleDescriptor:
        registry = cast(ModuleRegistry, request.app.state.module_registry)
        descriptor = registry.update_health(name, payload.health)
        if descriptor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="module not found")
        await publish_module_event(request, descriptor, EventName.HEALTH_CHANGED)
        return descriptor

    return router


def event_for_status(status: ModuleStatus) -> EventName:
    if status in {ModuleStatus.ONLINE, ModuleStatus.STARTING}:
        return EventName.MODULE_STARTED
    if status in {ModuleStatus.STOPPED, ModuleStatus.OFFLINE}:
        return EventName.MODULE_STOPPED
    return EventName.HEALTH_CHANGED


async def publish_module_event(
    request: Request,
    descriptor: ModuleDescriptor,
    event_name: EventName,
) -> None:
    event_bus = cast(EventBus, request.app.state.event_bus)
    if not event_bus.connected:
        return
    settings = request.app.state.settings
    await event_bus.publish(
        FoundationEvent(
            name=event_name,
            producer=settings.service_name,
            payload={
                "module": descriptor.name,
                "version": descriptor.version,
                "status": descriptor.status.value,
                "health": descriptor.health.status,
            },
        )
    )
