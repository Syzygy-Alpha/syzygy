from pathlib import Path

from syzygy_forge.database import Database
from syzygy_forge.project_creator import (
    ProjectCreationError,
    ProjectCreationRequest,
    ProjectCreator,
)
from syzygy_forge.project_registry import ProjectRegistry


def build_creator(workspace_root: Path) -> ProjectCreator:
    database = Database("sqlite:///:memory:")
    database.initialize()
    registry = ProjectRegistry(database)
    return ProjectCreator(workspace_root, registry)


def test_project_creator_creates_python_cli_project(tmp_path: Path) -> None:
    creator = build_creator(tmp_path)

    result = creator.create(ProjectCreationRequest(name="hello-tool"))

    project_path = tmp_path / "hello-tool"
    assert result.record.name == "hello-tool"
    assert result.record.path == str(project_path.resolve())
    assert result.template == "python-cli"
    assert result.git_initialized is False
    assert "README.md" in result.files
    assert "src/hello_tool/main.py" in result.files
    assert (project_path / "syzygy.project.toml").exists()
    assert "hello-tool is alive" in (project_path / "src" / "hello_tool" / "main.py").read_text(
        encoding="utf-8"
    )


def test_project_creator_rejects_invalid_project_name(tmp_path: Path) -> None:
    creator = build_creator(tmp_path)

    try:
        creator.create(ProjectCreationRequest(name="../outside"))
    except ProjectCreationError:
        return

    raise AssertionError("invalid project name should be rejected")


def test_project_creator_rejects_existing_project_path(tmp_path: Path) -> None:
    creator = build_creator(tmp_path)
    (tmp_path / "existing").mkdir()

    try:
        creator.create(ProjectCreationRequest(name="existing"))
    except ProjectCreationError:
        return

    raise AssertionError("existing project path should be rejected")


def test_project_creator_rejects_unknown_template(tmp_path: Path) -> None:
    creator = build_creator(tmp_path)

    try:
        creator.create(ProjectCreationRequest(name="demo", template="missing"))
    except ProjectCreationError:
        return

    raise AssertionError("unknown template should be rejected")
