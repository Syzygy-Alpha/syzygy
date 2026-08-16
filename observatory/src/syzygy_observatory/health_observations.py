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


class HealthObservationTrend(BaseModel):
    name: str
    total: int
    by_status: dict[str, int] = Field(default_factory=dict)
    first_observed_at: datetime
    latest_observed_at: datetime
    latest_status: str
    status_changes: int


class HealthObservationTrends(BaseModel):
    total_services: int
    trends: list[HealthObservationTrend] = Field(default_factory=list)


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

    def trends(self, name: str | None = None) -> HealthObservationTrends:
        where_sql = "WHERE name = ?" if name is not None else ""
        values = (name,) if name is not None else ()
        with self.database.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT *
                FROM observatory_health_observations
                {where_sql}
                ORDER BY name ASC, id ASC
                """,
                values,
            ).fetchall()

        grouped: dict[str, list[HealthObservationRecord]] = {}
        for row in rows:
            record = self._from_row(row)
            grouped.setdefault(record.name, []).append(record)

        trends = [
            self._trend_from_records(service_name, records)
            for service_name, records in grouped.items()
        ]
        return HealthObservationTrends(total_services=len(trends), trends=trends)

    def _trend_from_records(
        self,
        name: str,
        records: list[HealthObservationRecord],
    ) -> HealthObservationTrend:
        first = records[0]
        latest = records[-1]
        by_status: dict[str, int] = {}
        status_changes = 0
        previous_status: str | None = None
        for record in records:
            by_status[record.status] = by_status.get(record.status, 0) + 1
            if previous_status is not None and previous_status != record.status:
                status_changes += 1
            previous_status = record.status

        return HealthObservationTrend(
            name=name,
            total=len(records),
            by_status=by_status,
            first_observed_at=first.observed_at,
            latest_observed_at=latest.observed_at,
            latest_status=latest.status,
            status_changes=status_changes,
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
