import json
import sqlite3
from datetime import UTC, datetime
from typing import Any

from syzygy_foundation.modules.types import ModuleDescriptor, ModuleHealth, ModuleStatus
from syzygy_foundation.persistence import Database


class ModuleRegistry:
    def __init__(self, database: Database | None = None) -> None:
        self.database = database
        self._modules: dict[str, ModuleDescriptor] = {}

    def register(self, descriptor: ModuleDescriptor) -> None:
        descriptor = self._with_last_seen(descriptor)
        if self.database is not None:
            self._upsert(descriptor)
        self._modules[descriptor.name] = descriptor

    def list_modules(self) -> list[ModuleDescriptor]:
        if self.database is not None:
            with self.database.connect() as connection:
                rows = connection.execute(
                    "SELECT * FROM foundation_modules ORDER BY name"
                ).fetchall()
            return [self._from_row(row) for row in rows]
        return sorted(self._modules.values(), key=lambda module: module.name)

    def get(self, name: str) -> ModuleDescriptor | None:
        if self.database is not None:
            with self.database.connect() as connection:
                row = connection.execute(
                    "SELECT * FROM foundation_modules WHERE name = ?",
                    (name,),
                ).fetchone()
            return self._from_row(row) if row else None
        return self._modules.get(name)

    def update_status(self, name: str, status: ModuleStatus) -> ModuleDescriptor | None:
        descriptor = self.get(name)
        if descriptor is None:
            return None
        updated = descriptor.model_copy(
            update={"status": status, "last_seen_at": datetime.now(UTC)}
        )
        self.register(updated)
        return updated

    def update_health(self, name: str, health: ModuleHealth) -> ModuleDescriptor | None:
        descriptor = self.get(name)
        if descriptor is None:
            return None
        status = ModuleStatus.DEGRADED if health.status != "ok" else descriptor.status
        updated = descriptor.model_copy(
            update={"health": health, "status": status, "last_seen_at": datetime.now(UTC)}
        )
        self.register(updated)
        return updated

    def _upsert(self, descriptor: ModuleDescriptor) -> None:
        if self.database is None:
            msg = "persistent registry requires a database"
            raise RuntimeError(msg)
        database = self.database
        now = datetime.now(UTC).isoformat()
        last_seen_at = descriptor.last_seen_at or datetime.now(UTC)
        payload = (
            descriptor.name,
            descriptor.version,
            descriptor.status.value,
            descriptor.health.model_dump_json(),
            json.dumps(descriptor.capabilities),
            json.dumps(descriptor.dependencies),
            last_seen_at.isoformat(),
            now,
            now,
        )
        with database.connect() as connection:
            connection.execute(
                """
                INSERT INTO foundation_modules (
                    name,
                    version,
                    status,
                    health,
                    capabilities,
                    dependencies,
                    last_seen_at,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    version = excluded.version,
                    status = excluded.status,
                    health = excluded.health,
                    capabilities = excluded.capabilities,
                    dependencies = excluded.dependencies,
                    last_seen_at = excluded.last_seen_at,
                    updated_at = excluded.updated_at
                """,
                payload,
            )

    def _with_last_seen(self, descriptor: ModuleDescriptor) -> ModuleDescriptor:
        if descriptor.last_seen_at is not None:
            return descriptor
        return descriptor.model_copy(update={"last_seen_at": datetime.now(UTC)})

    def _from_row(self, row: sqlite3.Row) -> ModuleDescriptor:
        health_payload = self._load_json_object(row["health"])
        capabilities = self._load_json_list(row["capabilities"])
        dependencies = self._load_json_list(row["dependencies"])
        return ModuleDescriptor(
            name=row["name"],
            version=row["version"],
            status=ModuleStatus(row["status"]),
            health=ModuleHealth.model_validate(health_payload),
            capabilities=capabilities,
            dependencies=dependencies,
            last_seen_at=datetime.fromisoformat(row["last_seen_at"]),
        )

    def _load_json_object(self, value: str) -> dict[str, Any]:
        loaded = json.loads(value)
        if not isinstance(loaded, dict):
            msg = "stored JSON value is not an object"
            raise ValueError(msg)
        return loaded

    def _load_json_list(self, value: str) -> list[str]:
        loaded = json.loads(value)
        if not isinstance(loaded, list) or not all(isinstance(item, str) for item in loaded):
            msg = "stored JSON value is not a string list"
            raise ValueError(msg)
        return loaded
