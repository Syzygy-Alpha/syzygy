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
        name="forge_projects",
        sql="""
        CREATE TABLE IF NOT EXISTS forge_projects (
            name TEXT PRIMARY KEY,
            path TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """,
    ),
    Migration(
        version=2,
        name="forge_command_runs",
        sql="""
        CREATE TABLE IF NOT EXISTS forge_command_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT NOT NULL,
            command_name TEXT NOT NULL,
            command TEXT NOT NULL,
            cwd TEXT NOT NULL,
            allowed INTEGER NOT NULL,
            reason TEXT NOT NULL,
            returncode INTEGER,
            timed_out INTEGER NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_forge_command_runs_project
        ON forge_command_runs (project, id DESC);
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
                INSERT INTO forge_schema_migrations (version, name, applied_at)
                VALUES (?, ?, ?)
                """,
                (migration.version, migration.name, datetime.now(UTC).isoformat()),
            )
        connection.commit()

    def current_version(self, connection: sqlite3.Connection) -> int:
        self._ensure_migration_table(connection)
        row = connection.execute(
            "SELECT MAX(version) AS version FROM forge_schema_migrations"
        ).fetchone()
        version = row["version"] if row else None
        return int(version) if version is not None else 0

    def _ensure_migration_table(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS forge_schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL
            )
            """
        )

    def _applied_versions(self, connection: sqlite3.Connection) -> set[int]:
        rows = connection.execute("SELECT version FROM forge_schema_migrations").fetchall()
        return {int(row["version"]) for row in rows}
