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
from syzygy_foundation.health import HealthService
from syzygy_foundation.modules import ModuleDescriptor, ModuleRegistry


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

    @router.get("/modules")
    def modules(request: Request) -> list[ModuleDescriptor]:
        registry = request.app.state.module_registry
        return cast(ModuleRegistry, registry).list_modules()

    return router
