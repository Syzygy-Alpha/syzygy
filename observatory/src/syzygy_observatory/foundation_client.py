import httpx

from syzygy_observatory.module import ModuleDescriptor


class FoundationClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.transport = transport

    async def register_module(self, descriptor: ModuleDescriptor) -> None:
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=5.0,
            transport=self.transport,
        ) as client:
            token = await self._token(client)
            response = await client.post(
                "/modules/register",
                headers={"Authorization": f"Bearer {token}"},
                json=descriptor.model_dump(mode="json"),
            )
            response.raise_for_status()

    async def _token(self, client: httpx.AsyncClient) -> str:
        response = await client.post(
            "/auth/token",
            json={"username": self.username, "password": self.password},
        )
        response.raise_for_status()
        payload = response.json()
        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            msg = "Foundation token response did not include an access token"
            raise ValueError(msg)
        return token
