import sqlite3
from pathlib import Path
from urllib.parse import urlparse


class Database:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.path = self._sqlite_path(database_url)

    def initialize(self) -> None:
        if self.path != Path(":memory:"):
            self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS foundation_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT OR REPLACE INTO foundation_metadata (key, value)
                VALUES ('schema_version', '1')
                """
            )

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def ping(self) -> bool:
        with self.connect() as connection:
            row = connection.execute("SELECT 1 AS ok").fetchone()
        return bool(row and row["ok"] == 1)

    @staticmethod
    def _sqlite_path(database_url: str) -> Path:
        if database_url.startswith("sqlite:///:memory:"):
            return Path(":memory:")
        parsed = urlparse(database_url)
        if parsed.scheme != "sqlite":
            msg = "Foundation MVP supports sqlite database URLs only"
            raise ValueError(msg)
        if parsed.path in ("", "/"):
            return Path(":memory:")
        if parsed.netloc:
            return Path(f"//{parsed.netloc}{parsed.path}")
        if database_url.startswith("sqlite:///./"):
            return Path(database_url.removeprefix("sqlite:///"))
        if database_url.startswith("sqlite:///"):
            return Path(parsed.path)
        return Path(parsed.path)
