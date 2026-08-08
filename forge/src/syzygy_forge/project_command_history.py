import sqlite3
from datetime import datetime

from pydantic import BaseModel

from syzygy_forge.database import Database
from syzygy_forge.project_command_runner import ProjectCommandRunResult


class ProjectCommandRunRecord(BaseModel):
    id: int
    project: str
    command_name: str
    command: str
    cwd: str
    allowed: bool
    reason: str
    returncode: int | None
    timed_out: bool
    started_at: datetime
    completed_at: datetime


class ProjectCommandHistory:
    def __init__(self, database: Database) -> None:
        self.database = database

    def record(self, result: ProjectCommandRunResult) -> ProjectCommandRunRecord:
        plan = result.plan
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO forge_command_runs (
                    project,
                    command_name,
                    command,
                    cwd,
                    allowed,
                    reason,
                    returncode,
                    timed_out,
                    started_at,
                    completed_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    plan.project,
                    plan.command_name,
                    plan.command,
                    plan.cwd,
                    int(plan.allowed),
                    plan.reason,
                    result.returncode,
                    int(result.timed_out),
                    result.started_at.isoformat(),
                    result.completed_at.isoformat(),
                ),
            )
            connection.commit()
            if cursor.lastrowid is None:
                msg = "Command run insert did not return an id"
                raise RuntimeError(msg)
            run_id = int(cursor.lastrowid)

        return ProjectCommandRunRecord(
            id=run_id,
            project=plan.project,
            command_name=plan.command_name,
            command=plan.command,
            cwd=plan.cwd,
            allowed=plan.allowed,
            reason=plan.reason,
            returncode=result.returncode,
            timed_out=result.timed_out,
            started_at=result.started_at,
            completed_at=result.completed_at,
        )

    def list_for_project(self, project: str) -> list[ProjectCommandRunRecord]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM forge_command_runs
                WHERE project = ?
                ORDER BY id DESC
                """,
                (project,),
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def _from_row(self, row: sqlite3.Row) -> ProjectCommandRunRecord:
        return ProjectCommandRunRecord(
            id=row["id"],
            project=row["project"],
            command_name=row["command_name"],
            command=row["command"],
            cwd=row["cwd"],
            allowed=bool(row["allowed"]),
            reason=row["reason"],
            returncode=row["returncode"],
            timed_out=bool(row["timed_out"]),
            started_at=datetime.fromisoformat(row["started_at"]),
            completed_at=datetime.fromisoformat(row["completed_at"]),
        )
