import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    sql: str


MIGRATIONS: tuple[Migration, ...] = (
    Migration(
        version=1,
        name="foundation_metadata",
        sql="""
        CREATE TABLE IF NOT EXISTS foundation_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        INSERT OR REPLACE INTO foundation_metadata (key, value)
        VALUES ('schema_version', '1');
        """,
    ),
    Migration(
        version=2,
        name="foundation_modules",
        sql="""
        CREATE TABLE IF NOT EXISTS foundation_modules (
            name TEXT PRIMARY KEY,
            version TEXT NOT NULL,
            status TEXT NOT NULL,
            health TEXT NOT NULL,
            capabilities TEXT NOT NULL,
            dependencies TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        INSERT OR REPLACE INTO foundation_metadata (key, value)
        VALUES ('schema_version', '2');
        """,
    ),
)


class MigrationRunner:
    def __init__(self, migrations: tuple[Migration, ...] = MIGRATIONS) -> None:
        self.migrations = tuple(sorted(migrations, key=lambda migration: migration.version))

    def apply(self, connection: sqlite3.Connection) -> None:
        self._ensure_migration_table(connection)
        applied_versions = self._applied_versions(connection)
        for migration in self.migrations:
            if migration.version in applied_versions:
                continue
            connection.executescript(migration.sql)
            connection.execute(
                """
                INSERT INTO foundation_schema_migrations (version, name, applied_at)
                VALUES (?, ?, ?)
                """,
                (migration.version, migration.name, datetime.now(UTC).isoformat()),
            )
        connection.commit()

    def current_version(self, connection: sqlite3.Connection) -> int:
        self._ensure_migration_table(connection)
        row = connection.execute(
            "SELECT MAX(version) AS version FROM foundation_schema_migrations"
        ).fetchone()
        version = row["version"] if row else None
        return int(version) if version is not None else 0

    def _ensure_migration_table(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS foundation_schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL
            )
            """
        )

    def _applied_versions(self, connection: sqlite3.Connection) -> set[int]:
        rows = connection.execute("SELECT version FROM foundation_schema_migrations").fetchall()
        return {int(row["version"]) for row in rows}
