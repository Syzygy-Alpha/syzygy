from pathlib import Path

import pytest

from syzygy_foundation.modules import ModuleDescriptor, ModuleHealth, ModuleRegistry, ModuleStatus
from syzygy_foundation.persistence import Database


def test_module_registry_persists_registered_modules(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    database = Database("sqlite:///./foundation.db")
    database.initialize()
    registry = ModuleRegistry(database)

    registry.register(
        ModuleDescriptor(
            name="forge",
            version="0.1.0",
            status=ModuleStatus.OFFLINE,
            health=ModuleHealth(status="unknown"),
            capabilities=["git", "build"],
            dependencies=["foundation"],
        )
    )

    loaded = registry.get("forge")

    assert loaded is not None
    assert loaded.name == "forge"
    assert loaded.capabilities == ["git", "build"]
    assert loaded.dependencies == ["foundation"]
    assert loaded.last_seen_at is not None


def test_module_registry_updates_status_and_health(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    database = Database("sqlite:///./foundation.db")
    database.initialize()
    registry = ModuleRegistry(database)
    registry.register(
        ModuleDescriptor(
            name="observatory",
            version="0.1.0",
            status=ModuleStatus.ONLINE,
            health=ModuleHealth(status="ok"),
        )
    )

    status = registry.update_status("observatory", ModuleStatus.STOPPED)
    health = registry.update_health(
        "observatory",
        ModuleHealth(status="error", details={"reason": "collector unavailable"}),
    )

    assert status is not None
    assert status.status == ModuleStatus.STOPPED
    assert health is not None
    assert health.status == ModuleStatus.DEGRADED
    assert health.health.details == {"reason": "collector unavailable"}

