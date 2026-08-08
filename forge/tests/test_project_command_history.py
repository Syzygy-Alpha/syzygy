import sys
from pathlib import Path

from syzygy_forge.database import Database
from syzygy_forge.project_command_history import ProjectCommandHistory
from syzygy_forge.project_command_planner import ProjectCommandPlan
from syzygy_forge.project_command_runner import ProjectCommandRunner, ProjectCommandRunRequest


def build_history() -> ProjectCommandHistory:
    database = Database("sqlite:///:memory:")
    database.initialize()
    return ProjectCommandHistory(database)


def build_plan(tmp_path: Path, project: str = "demo") -> ProjectCommandPlan:
    return ProjectCommandPlan(
        project=project,
        command_name="hello",
        command='python -c "print(123)"',
        cwd=str(tmp_path),
        argv=[sys.executable, "-c", "print(123)"],
        allowed=True,
        reason="allowed",
    )


def test_project_command_history_records_run_metadata(tmp_path: Path) -> None:
    history = build_history()
    runner = ProjectCommandRunner()
    result = runner.run(build_plan(tmp_path), ProjectCommandRunRequest(confirm=True))

    record = history.record(result)

    assert record.id == 1
    assert record.project == "demo"
    assert record.command_name == "hello"
    assert record.returncode == 0
    assert record.timed_out is False


def test_project_command_history_lists_project_runs_newest_first(tmp_path: Path) -> None:
    history = build_history()
    runner = ProjectCommandRunner()

    first = runner.run(build_plan(tmp_path, "demo"), ProjectCommandRunRequest(confirm=True))
    other = runner.run(build_plan(tmp_path, "other"), ProjectCommandRunRequest(confirm=True))
    second = runner.run(build_plan(tmp_path, "demo"), ProjectCommandRunRequest(confirm=True))
    history.record(first)
    history.record(other)
    history.record(second)

    records = history.list_for_project("demo")

    assert [record.id for record in records] == [3, 1]
    assert all(record.project == "demo" for record in records)
