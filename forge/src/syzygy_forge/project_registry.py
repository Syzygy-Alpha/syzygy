import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from syzygy_forge.database import Database
from syzygy_forge.project_inspector import ProjectInspection


class ProjectRegistrationRequest(BaseModel):
    path: Path
    name: str | None = Field(default=None, min_length=1)


class ProjectRecord(BaseModel):
    name: str
    path: str
    created_at: datetime
    updated_at: datetime


class ProjectDetails(BaseModel):
    record: ProjectRecord
    inspection: ProjectInspection


class ProjectPathError(ValueError):
    pass


class ProjectRegistry:
    def __init__(self, database: Database) -> None:
        self.database = database

    def register(self, path: Path, name: str | None = None) -> ProjectRecord:
        resolved = path.resolve()
        if not resolved.exists():
            msg = f"Project path does not exist: {resolved}"
            raise ProjectPathError(msg)

        project_name = (name or resolved.name).strip()
        if not project_name:
            msg = "Project name cannot be empty"
            raise ProjectPathError(msg)

        now = datetime.now(UTC)
        with self.database.connect() as connection:
            existing = connection.execute(
                "SELECT created_at FROM forge_projects WHERE name = ?",
                (project_name,),
            ).fetchone()
            created_at = datetime.fromisoformat(existing["created_at"]) if existing else now
            connection.execute(
                """
                INSERT INTO forge_projects (name, path, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    path = excluded.path,
                    updated_at = excluded.updated_at
                """,
                (project_name, str(resolved), created_at.isoformat(), now.isoformat()),
            )
            connection.commit()

        return ProjectRecord(
            name=project_name,
            path=str(resolved),
            created_at=created_at,
            updated_at=now,
        )

    def list_projects(self) -> list[ProjectRecord]:
        with self.database.connect() as connection:
            rows = connection.execute("SELECT * FROM forge_projects ORDER BY name").fetchall()
        return [self._from_row(row) for row in rows]

    def get(self, name: str) -> ProjectRecord | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM forge_projects WHERE name = ?",
                (name,),
            ).fetchone()
        return self._from_row(row) if row else None

    def _from_row(self, row: sqlite3.Row) -> ProjectRecord:
        return ProjectRecord(
            name=row["name"],
            path=row["path"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
