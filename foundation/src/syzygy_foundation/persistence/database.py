import sqlite3
from pathlib import Path
from urllib.parse import urlparse

from syzygy_foundation.persistence.migrations import MigrationRunner


class Database:
    def __init__(self, database_url: str, migration_runner: MigrationRunner | None = None) -> None:
        self.database_url = database_url
        self.path = self._sqlite_path(database_url)
        self.migration_runner = migration_runner or MigrationRunner()

    def initialize(self) -> None:
        if self.path != Path(":memory:"):
            self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            self.migration_runner.apply(connection)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def ping(self) -> bool:
        with self.connect() as connection:
            row = connection.execute("SELECT 1 AS ok").fetchone()
        return bool(row and row["ok"] == 1)

    def schema_version(self) -> int:
        with self.connect() as connection:
            return self.migration_runner.current_version(connection)

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
