from datetime import UTC, datetime
from pathlib import Path

from syzygy_forge.project_manifest import ProjectManifestError, ProjectManifestReader
from syzygy_forge.project_registry import ProjectRecord


def build_record(path: Path) -> ProjectRecord:
    return ProjectRecord(
        name="demo",
        path=str(path),
        created_at=datetime(2026, 8, 8, tzinfo=UTC),
        updated_at=datetime(2026, 8, 8, tzinfo=UTC),
    )


def test_project_manifest_reader_discovers_commands(tmp_path: Path) -> None:
    (tmp_path / "syzygy.project.toml").write_text(
        """
name = "demo"

[commands]
test = "python -m pytest"
lint = "python -m ruff check ."
""",
        encoding="utf-8",
    )
    reader = ProjectManifestReader()

    command_set = reader.commands_for(build_record(tmp_path))

    assert command_set.project == "demo"
    assert [command.name for command in command_set.commands] == ["lint", "test"]
    assert command_set.commands[1].command == "python -m pytest"


def test_project_manifest_reader_rejects_missing_manifest(tmp_path: Path) -> None:
    reader = ProjectManifestReader()

    try:
        reader.commands_for(build_record(tmp_path))
    except ProjectManifestError:
        return

    raise AssertionError("missing manifest should be rejected")


def test_project_manifest_reader_rejects_non_string_commands(tmp_path: Path) -> None:
    (tmp_path / "syzygy.project.toml").write_text(
        """
name = "demo"

[commands]
test = ["python", "-m", "pytest"]
""",
        encoding="utf-8",
    )
    reader = ProjectManifestReader()

    try:
        reader.commands_for(build_record(tmp_path))
    except ProjectManifestError:
        return

    raise AssertionError("non-string command should be rejected")
