import json
import sqlite3
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from syzygy_mycelium.database import Database


class PeerRegistrationRequest(BaseModel):
    node_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    agent: str = Field(default="hypha", min_length=1)
    status: str = Field(default="known", min_length=1)
    source: str = Field(default="manual", min_length=1)
    capabilities: list[str] = Field(default_factory=list)


class PeerRecord(BaseModel):
    node_id: str
    name: str
    address: str
    agent: str
    status: str
    source: str
    capabilities: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class PeerRegistryError(ValueError):
    pass


class PeerRegistry:
    def __init__(self, database: Database) -> None:
        self.database = database

    def register(self, request: PeerRegistrationRequest) -> PeerRecord:
        node_id = request.node_id.strip()
        name = request.name.strip()
        address = request.address.strip()
        agent = request.agent.strip()
        status = request.status.strip()
        source = request.source.strip()
        capabilities = self._normalize_capabilities(request.capabilities)

        if not node_id:
            msg = "Peer node_id cannot be empty"
            raise PeerRegistryError(msg)
        if not name:
            msg = "Peer name cannot be empty"
            raise PeerRegistryError(msg)
        if not address:
            msg = "Peer address cannot be empty"
            raise PeerRegistryError(msg)
        if not agent:
            msg = "Peer agent cannot be empty"
            raise PeerRegistryError(msg)
        if not status:
            msg = "Peer status cannot be empty"
            raise PeerRegistryError(msg)
        if not source:
            msg = "Peer source cannot be empty"
            raise PeerRegistryError(msg)

        now = datetime.now(UTC)
        with self.database.connect() as connection:
            existing = connection.execute(
                "SELECT created_at FROM mycelium_peers WHERE node_id = ?",
                (node_id,),
            ).fetchone()
            created_at = datetime.fromisoformat(existing["created_at"]) if existing else now
            connection.execute(
                """
                INSERT INTO mycelium_peers (
                    node_id,
                    name,
                    address,
                    agent,
                    status,
                    source,
                    capabilities,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(node_id) DO UPDATE SET
                    name = excluded.name,
                    address = excluded.address,
                    agent = excluded.agent,
                    status = excluded.status,
                    source = excluded.source,
                    capabilities = excluded.capabilities,
                    updated_at = excluded.updated_at
                """,
                (
                    node_id,
                    name,
                    address,
                    agent,
                    status,
                    source,
                    json.dumps(capabilities),
                    created_at.isoformat(),
                    now.isoformat(),
                ),
            )
            connection.commit()

        return PeerRecord(
            node_id=node_id,
            name=name,
            address=address,
            agent=agent,
            status=status,
            source=source,
            capabilities=capabilities,
            created_at=created_at,
            updated_at=now,
        )

    def list_peers(self) -> list[PeerRecord]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM mycelium_peers ORDER BY name, node_id"
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def get(self, node_id: str) -> PeerRecord | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM mycelium_peers WHERE node_id = ?",
                (node_id,),
            ).fetchone()
        return self._from_row(row) if row else None

    def _from_row(self, row: sqlite3.Row) -> PeerRecord:
        capabilities = json.loads(row["capabilities"])
        if not isinstance(capabilities, list):
            capabilities = []
        return PeerRecord(
            node_id=row["node_id"],
            name=row["name"],
            address=row["address"],
            agent=row["agent"],
            status=row["status"],
            source=row["source"],
            capabilities=[str(value) for value in capabilities],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def _normalize_capabilities(self, capabilities: list[str]) -> list[str]:
        normalized: list[str] = []
        for capability in capabilities:
            value = capability.strip()
            if value and value not in normalized:
                normalized.append(value)
        return normalized
