import json
import sqlite3
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

from syzygy_forge.database import Database
from syzygy_forge.events import ForgeEvent


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
    created_at: datetime


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
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            created_at=now,
        )

    def enqueue_many(self, events: list[ForgeEvent]) -> list[ForgeEventOutboxRecord]:
        return [self.enqueue(event) for event in events]

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
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _load_payload(self, value: str) -> dict[str, Any]:
        loaded = json.loads(value)
        if not isinstance(loaded, dict):
            msg = "stored event payload is not an object"
            raise ValueError(msg)
        return loaded
