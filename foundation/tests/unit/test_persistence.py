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
