from datetime import UTC, datetime
from pathlib import Path

from syzygy_forge.project_command_planner import ProjectCommandPlanner
from syzygy_forge.project_manifest import ProjectCommand, ProjectCommandSet
from syzygy_forge.project_registry import ProjectRecord


def build_record(path: Path) -> ProjectRecord:
    return ProjectRecord(
        name="demo",
        path=str(path),
        created_at=datetime(2026, 8, 8, tzinfo=UTC),
        updated_at=datetime(2026, 8, 8, tzinfo=UTC),
    )


def build_command_set(*commands: ProjectCommand) -> ProjectCommandSet:
    return ProjectCommandSet(
        project="demo",
        manifest_path="syzygy.project.toml",
        commands=list(commands),
    )


def test_project_command_planner_allows_python_command(tmp_path: Path) -> None:
    planner = ProjectCommandPlanner()
    command_set = build_command_set(ProjectCommand(name="test", command="python -m pytest"))

    plan = planner.plan(build_record(tmp_path), command_set, "test")

    assert plan.allowed is True
    assert plan.reason == "allowed"
    assert plan.argv == ["python", "-m", "pytest"]
    assert plan.cwd == str(tmp_path.resolve())


def test_project_command_planner_blocks_shell_control_syntax(tmp_path: Path) -> None:
    planner = ProjectCommandPlanner()
    command_set = build_command_set(
        ProjectCommand(name="test", command="python -m pytest && git status")
    )

    plan = planner.plan(build_record(tmp_path), command_set, "test")

    assert plan.allowed is False
    assert plan.reason == "command contains shell control syntax"


def test_project_command_planner_blocks_unknown_executable(tmp_path: Path) -> None:
    planner = ProjectCommandPlanner()
    command_set = build_command_set(ProjectCommand(name="deploy", command="powershell deploy.ps1"))

    plan = planner.plan(build_record(tmp_path), command_set, "deploy")

    assert plan.allowed is False
    assert plan.reason == "command executable is not allowed"


def test_project_command_planner_reports_missing_command(tmp_path: Path) -> None:
    planner = ProjectCommandPlanner()
    command_set = build_command_set(ProjectCommand(name="test", command="python -m pytest"))

    plan = planner.plan(build_record(tmp_path), command_set, "missing")

    assert plan.allowed is False
    assert plan.reason == "Project command not found"
