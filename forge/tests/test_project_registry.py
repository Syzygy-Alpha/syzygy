from pathlib import Path

from syzygy_forge.database import Database
from syzygy_forge.project_registry import ProjectPathError, ProjectRegistry


def build_registry() -> ProjectRegistry:
    database = Database("sqlite:///:memory:")
    database.initialize()
    return ProjectRegistry(database)


def test_project_registry_registers_existing_project(tmp_path: Path) -> None:
    registry = build_registry()

    record = registry.register(tmp_path, "syzygy")

    assert record.name == "syzygy"
    assert record.path == str(tmp_path.resolve())
    assert registry.get("syzygy") == record


def test_project_registry_lists_projects_by_name(tmp_path: Path) -> None:
    alpha = tmp_path / "alpha"
    beta = tmp_path / "beta"
    alpha.mkdir()
    beta.mkdir()
    registry = build_registry()

    registry.register(beta)
    registry.register(alpha)

    assert [project.name for project in registry.list_projects()] == ["alpha", "beta"]


def test_project_registry_updates_existing_project(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    registry = build_registry()

    original = registry.register(first, "syzygy")
    updated = registry.register(second, "syzygy")

    assert updated.path == str(second.resolve())
    assert updated.created_at == original.created_at
    assert updated.updated_at >= original.updated_at


def test_project_registry_rejects_missing_path(tmp_path: Path) -> None:
    registry = build_registry()

    try:
        registry.register(tmp_path / "missing", "missing")
    except ProjectPathError:
        return

    raise AssertionError("missing project path should be rejected")
