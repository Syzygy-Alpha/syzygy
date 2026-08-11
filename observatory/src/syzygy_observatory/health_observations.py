import json
import sqlite3
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from syzygy_observatory.database import Database


class HealthObservationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    status: str = Field(min_length=1, max_length=64)
    source: str = Field(default="manual", min_length=1, max_length=128)
    details: dict[str, str] = Field(default_factory=dict)
    observed_at: datetime | None = None


class HealthObservationRecord(BaseModel):
    id: int
    name: str
    status: str
    source: str
    details: dict[str, str]
    observed_at: datetime
    created_at: datetime


class HealthObservationSummary(BaseModel):
    total: int
    by_status: dict[str, int] = Field(default_factory=dict)
    latest_by_name: list[HealthObservationRecord] = Field(default_factory=list)


class HealthObservationStore:
    def __init__(self, database: Database) -> None:
        self.database = database

    def record(self, request: HealthObservationRequest) -> HealthObservationRecord:
        now = datetime.now(UTC)
        observed_at = request.observed_at or now
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO observatory_health_observations (
                    name,
                    status,
                    source,
                    details,
                    observed_at,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    request.name,
                    request.status,
                    request.source,
                    json.dumps(request.details),
                    observed_at.isoformat(),
                    now.isoformat(),
                ),
            )
            connection.commit()
            if cursor.lastrowid is None:
                msg = "Health observation insert did not return an id"
                raise RuntimeError(msg)
            record_id = int(cursor.lastrowid)

        return HealthObservationRecord(
            id=record_id,
            name=request.name,
            status=request.status,
            source=request.source,
            details=request.details,
            observed_at=observed_at,
            created_at=now,
        )

    def list_observations(
        self,
        name: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[HealthObservationRecord]:
        where_clauses = []
        values: list[str | int] = []
        if name is not None:
            where_clauses.append("name = ?")
            values.append(name)
        if status is not None:
            where_clauses.append("status = ?")
            values.append(status)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        values.append(limit)
        with self.database.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT * FROM observatory_health_observations
                {where_sql}
                ORDER BY id DESC
                LIMIT ?
                """,
                tuple(values),
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def summary(self) -> HealthObservationSummary:
        with self.database.connect() as connection:
            total_row = connection.execute(
                "SELECT COUNT(*) AS total FROM observatory_health_observations"
            ).fetchone()
            count_rows = connection.execute(
                """
                SELECT status, COUNT(*) AS count
                FROM observatory_health_observations
                GROUP BY status
                """
            ).fetchall()
            latest_rows = connection.execute(
                """
                SELECT observations.*
                FROM observatory_health_observations observations
                JOIN (
                    SELECT name, MAX(id) AS id
                    FROM observatory_health_observations
                    GROUP BY name
                ) latest
                ON observations.name = latest.name
                AND observations.id = latest.id
                ORDER BY observations.name
                """
            ).fetchall()

        return HealthObservationSummary(
            total=int(total_row["total"]),
            by_status={row["status"]: int(row["count"]) for row in count_rows},
            latest_by_name=[self._from_row(row) for row in latest_rows],
        )

    def _from_row(self, row: sqlite3.Row) -> HealthObservationRecord:
        return HealthObservationRecord(
            id=row["id"],
            name=row["name"],
            status=row["status"],
            source=row["source"],
            details=self._load_details(row["details"]),
            observed_at=datetime.fromisoformat(row["observed_at"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _load_details(self, value: str) -> dict[str, str]:
        loaded = json.loads(value)
        if not isinstance(loaded, dict):
            msg = "stored health observation details are not an object"
            raise ValueError(msg)
        return {str(key): str(item) for key, item in loaded.items()}
