import json
import sqlite3
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from syzygy_forge.database import Database
from syzygy_forge.events import ForgeEvent


class EventOutboxError(ValueError):
    pass


class EventOutboxRecordNotFoundError(EventOutboxError):
    pass


class EventOutboxStatusError(EventOutboxError):
    pass


class ForgeEventOutboxRecord(BaseModel):
    id: int
    event_id: str
    name: str
    subject: str
    producer: str
    payload: dict[str, Any]
    version: str
    occurred_at: datetime
    status: str
    attempts: int = 0
    last_error: str | None = None
    published_at: datetime | None = None
    created_at: datetime


class EventRequeueRequest(BaseModel):
    confirm: bool = Field(default=False)


class EventRequeueFailedRequest(EventRequeueRequest):
    limit: int = Field(default=100, ge=1, le=500)


class EventRequeueResult(BaseModel):
    requeued: int
    events: list[ForgeEventOutboxRecord] = Field(default_factory=list)


class ForgeEventOutbox:
    def __init__(self, database: Database) -> None:
        self.database = database

    def enqueue(self, event: ForgeEvent, status: str = "pending") -> ForgeEventOutboxRecord:
        now = datetime.now(UTC)
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO forge_event_outbox (
                    event_id,
                    name,
                    subject,
                    producer,
                    payload,
                    version,
                    occurred_at,
                    status,
                    attempts,
                    last_error,
                    published_at,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.name.value,
                    event.subject(),
                    event.producer,
                    json.dumps(event.payload),
                    event.version,
                    event.occurred_at.isoformat(),
                    status,
                    0,
                    None,
                    None,
                    now.isoformat(),
                ),
            )
            connection.commit()
            if cursor.lastrowid is None:
                msg = "Event outbox insert did not return an id"
                raise RuntimeError(msg)
            record_id = int(cursor.lastrowid)

        return ForgeEventOutboxRecord(
            id=record_id,
            event_id=event.id,
            name=event.name.value,
            subject=event.subject(),
            producer=event.producer,
            payload=event.payload,
            version=event.version,
            occurred_at=event.occurred_at,
            status=status,
            attempts=0,
            last_error=None,
            published_at=None,
            created_at=now,
        )

    def enqueue_many(self, events: list[ForgeEvent]) -> list[ForgeEventOutboxRecord]:
        return [self.enqueue(event) for event in events]

    def pending(self, limit: int = 100) -> list[ForgeEventOutboxRecord]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM forge_event_outbox
                WHERE status = 'pending'
                ORDER BY id
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def failed(self, limit: int = 100) -> list[ForgeEventOutboxRecord]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM forge_event_outbox
                WHERE status = 'failed'
                ORDER BY id
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def mark_published(self, record_id: int) -> ForgeEventOutboxRecord:
        published_at = datetime.now(UTC)
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE forge_event_outbox
                SET status = 'published',
                    attempts = attempts + 1,
                    last_error = NULL,
                    published_at = ?
                WHERE id = ?
                """,
                (published_at.isoformat(), record_id),
            )
            connection.commit()
        record = self.get(record_id)
        if record is None:
            msg = f"Event outbox record not found after publishing: {record_id}"
            raise RuntimeError(msg)
        return record

    def mark_failed(self, record_id: int, error: str) -> ForgeEventOutboxRecord:
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE forge_event_outbox
                SET status = 'failed',
                    attempts = attempts + 1,
                    last_error = ?,
                    published_at = NULL
                WHERE id = ?
                """,
                (error, record_id),
            )
            connection.commit()
        record = self.get(record_id)
        if record is None:
            msg = f"Event outbox record not found after failure: {record_id}"
            raise RuntimeError(msg)
        return record

    def get(self, record_id: int) -> ForgeEventOutboxRecord | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM forge_event_outbox WHERE id = ?",
                (record_id,),
            ).fetchone()
        return self._from_row(row) if row else None

    def requeue(self, record_id: int) -> ForgeEventOutboxRecord:
        record = self.get(record_id)
        if record is None:
            msg = f"Event outbox record not found: {record_id}"
            raise EventOutboxRecordNotFoundError(msg)
        if record.status != "failed":
            msg = f"Only failed event outbox records can be requeued: {record_id}"
            raise EventOutboxStatusError(msg)

        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE forge_event_outbox
                SET status = 'pending',
                    last_error = NULL,
                    published_at = NULL
                WHERE id = ?
                """,
                (record_id,),
            )
            connection.commit()
        requeued = self.get(record_id)
        if requeued is None:
            msg = f"Event outbox record not found after requeue: {record_id}"
            raise RuntimeError(msg)
        return requeued

    def requeue_failed(self, limit: int = 100) -> list[ForgeEventOutboxRecord]:
        return [self.requeue(record.id) for record in self.failed(limit)]

    def list_events(self, status: str | None = None) -> list[ForgeEventOutboxRecord]:
        with self.database.connect() as connection:
            if status is None:
                rows = connection.execute(
                    "SELECT * FROM forge_event_outbox ORDER BY id"
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT * FROM forge_event_outbox
                    WHERE status = ?
                    ORDER BY id
                    """,
                    (status,),
                ).fetchall()
        return [self._from_row(row) for row in rows]

    def _from_row(self, row: sqlite3.Row) -> ForgeEventOutboxRecord:
        return ForgeEventOutboxRecord(
            id=row["id"],
            event_id=row["event_id"],
            name=row["name"],
            subject=row["subject"],
            producer=row["producer"],
            payload=self._load_payload(row["payload"]),
            version=row["version"],
            occurred_at=datetime.fromisoformat(row["occurred_at"]),
            status=row["status"],
            attempts=row["attempts"],
            last_error=row["last_error"],
            published_at=self._datetime_or_none(row["published_at"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _load_payload(self, value: str) -> dict[str, Any]:
        loaded = json.loads(value)
        if not isinstance(loaded, dict):
            msg = "stored event payload is not an object"
            raise ValueError(msg)
        return loaded

    def _datetime_or_none(self, value: str | None) -> datetime | None:
        if value is None:
            return None
        return datetime.fromisoformat(value)
