from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import BaseModel, Field

from syzygy_nerv.catalog import SurfaceCatalog


class SurfaceActionResult(BaseModel):
    surface: str
    action: str
    label: str
    method: str
    url: str
    ok: bool
    status_code: int | None = None
    content_type: str | None = None
    received_at: datetime
    payload: Any | None = None
    error: str | None = None


class SurfaceActionError(ValueError):
    pass


class SurfaceActionExecutor:
    def __init__(
        self,
        catalog: SurfaceCatalog,
        timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.catalog = catalog
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    async def execute(self, surface_name: str, action_name: str) -> SurfaceActionResult:
        entry = self.catalog.get(surface_name)
        if entry is None:
            msg = f"Unknown surface: {surface_name}"
            raise SurfaceActionError(msg)

        action = next((item for item in entry.actions if item.name == action_name), None)
        if action is None:
            msg = f"Unknown action for surface {surface_name}: {action_name}"
            raise SurfaceActionError(msg)

        url = self._build_url(entry.links.root_url, action.path)
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout_seconds,
                transport=self.transport,
            ) as client:
                response = await client.request(
                    action.method.upper(),
                    url,
                    json=action.body or None,
                )
        except Exception as exc:
            return SurfaceActionResult(
                surface=surface_name,
                action=action.name,
                label=action.label,
                method=action.method.upper(),
                url=url,
                ok=False,
                received_at=datetime.now(UTC),
                error=str(exc),
            )

        content_type = response.headers.get("content-type")
        payload = self._payload(response)
        return SurfaceActionResult(
            surface=surface_name,
            action=action.name,
            label=action.label,
            method=action.method.upper(),
            url=url,
            ok=response.is_success,
            status_code=response.status_code,
            content_type=content_type,
            received_at=datetime.now(UTC),
            payload=payload,
            error=None if response.is_success else self._error_message(payload, response),
        )

    def _build_url(self, root_url: str, path: str) -> str:
        return f"{root_url.rstrip('/')}/{path.lstrip('/')}"

    def _payload(self, response: httpx.Response) -> Any:
        content_type = response.headers.get("content-type", "")
        if content_type.startswith("application/json"):
            return response.json()
        text = response.text
        return text if len(text) <= 4000 else f"{text[:4000]}\n...[truncated]"

    def _error_message(self, payload: Any, response: httpx.Response) -> str:
        if isinstance(payload, dict):
            detail = payload.get("detail")
            if isinstance(detail, str) and detail:
                return detail
        return f"HTTP {response.status_code}"
