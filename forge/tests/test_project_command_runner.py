import sys
from pathlib import Path

from syzygy_forge.project_command_planner import ProjectCommandPlan
from syzygy_forge.project_command_runner import (
    ProjectCommandExecutionError,
    ProjectCommandRunner,
    ProjectCommandRunRequest,
)


def build_plan(tmp_path: Path, allowed: bool = True) -> ProjectCommandPlan:
    return ProjectCommandPlan(
        project="demo",
        command_name="hello",
        command="python -c \"print('hello forge')\"",
        cwd=str(tmp_path),
        argv=[sys.executable, "-c", "print('hello forge')"],
        allowed=allowed,
        reason="allowed" if allowed else "blocked",
    )


def test_project_command_runner_executes_confirmed_allowed_plan(tmp_path: Path) -> None:
    runner = ProjectCommandRunner()

    result = runner.run(build_plan(tmp_path), ProjectCommandRunRequest(confirm=True))

    assert result.returncode == 0
    assert result.stdout.strip() == "hello forge"
    assert result.timed_out is False


def test_project_command_runner_requires_confirmation(tmp_path: Path) -> None:
    runner = ProjectCommandRunner()

    try:
        runner.run(build_plan(tmp_path), ProjectCommandRunRequest(confirm=False))
    except ProjectCommandExecutionError:
        return

    raise AssertionError("command execution should require confirmation")


def test_project_command_runner_rejects_blocked_plan(tmp_path: Path) -> None:
    runner = ProjectCommandRunner()

    try:
        runner.run(build_plan(tmp_path, allowed=False), ProjectCommandRunRequest(confirm=True))
    except ProjectCommandExecutionError:
        return

    raise AssertionError("blocked command plan should not execute")
