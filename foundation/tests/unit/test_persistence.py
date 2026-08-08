from pathlib import Path

import pytest

from syzygy_foundation.persistence import Database


def test_database_initializes_and_pings(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    database = Database("sqlite:///./foundation.db")

    database.initialize()

    assert database.ping() is True
    assert (tmp_path / "foundation.db").exists()
    assert database.schema_version() == 2


def test_database_tracks_applied_migrations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    database = Database("sqlite:///./foundation.db")

    database.initialize()
    database.initialize()

    with database.connect() as connection:
        rows = connection.execute(
            "SELECT version, name FROM foundation_schema_migrations"
        ).fetchall()

    assert [dict(row) for row in rows] == [
        {"version": 1, "name": "foundation_metadata"},
        {"version": 2, "name": "foundation_modules"},
    ]
