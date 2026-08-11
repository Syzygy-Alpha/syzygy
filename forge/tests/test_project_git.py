from datetime import UTC, datetime
from pathlib import Path

import pytest

from syzygy_forge.project_git import (
    GitAutomationError,
    GitBranchCreateRequest,
    GitCommandResult,
    GitCommitRequest,
    ProjectGitAutomation,
)
from syzygy_forge.project_registry import ProjectRecord


class FakeProjectGitAutomation(ProjectGitAutomation):
    def __init__(self, results: dict[tuple[str, ...], list[GitCommandResult]]) -> None:
        self.results = results
        self.calls: list[tuple[str, ...]] = []

    def _git(self, cwd: Path, *args: str) -> GitCommandResult:
        self.calls.append(args)
        command_results = self.results.get(args)
        if command_results:
            return command_results.pop(0)
        return GitCommandResult(returncode=1, stdout="", stderr="missing fake result")


def result(returncode: int = 0, stdout: str = "", stderr: str = "") -> GitCommandResult:
    return GitCommandResult(returncode=returncode, stdout=stdout, stderr=stderr)


def build_record(path: Path) -> ProjectRecord:
    return ProjectRecord(
        name="demo",
        path=str(path),
        created_at=datetime(2026, 8, 11, tzinfo=UTC),
        updated_at=datetime(2026, 8, 11, tzinfo=UTC),
    )


def test_project_git_status_reports_non_repository(tmp_path: Path) -> None:
    git = FakeProjectGitAutomation(
        {("rev-parse", "--is-inside-work-tree"): [result(returncode=1, stderr="not a repo")]}
    )

    status = git.status(build_record(tmp_path))

    assert status.is_repository is False
    assert status.dirty is False
    assert status.files == []


def test_project_git_status_reports_branch_commit_and_files(tmp_path: Path) -> None:
    git = FakeProjectGitAutomation(
        {
            ("rev-parse", "--is-inside-work-tree"): [result(stdout="true\n")],
            ("branch", "--show-current"): [result(stdout="main\n")],
            ("rev-parse", "--short", "HEAD"): [result(stdout="abc123\n")],
            ("status", "--porcelain=v1"): [
                result(stdout=" M README.md\nA  src/app.py\n?? notes.md\n")
            ],
        }
    )

    status = git.status(build_record(tmp_path))

    assert status.is_repository is True
    assert status.branch == "main"
    assert status.commit == "abc123"
    assert status.dirty is True
    assert [(item.index, item.worktree, item.path) for item in status.files] == [
        (" ", "M", "README.md"),
        ("A", " ", "src/app.py"),
        ("?", "?", "notes.md"),
    ]


def test_project_git_create_branch_requires_confirmation(tmp_path: Path) -> None:
    git = FakeProjectGitAutomation({})

    with pytest.raises(GitAutomationError, match="confirm=true"):
        git.create_branch(
            build_record(tmp_path),
            GitBranchCreateRequest(name="feature/demo", confirm=False),
        )


def test_project_git_create_branch_switches_to_new_branch(tmp_path: Path) -> None:
    git = FakeProjectGitAutomation(
        {
            ("rev-parse", "--is-inside-work-tree"): [result(stdout="true\n")],
            ("switch", "-c", "feature/demo"): [result(stdout="")],
            ("branch", "--show-current"): [result(stdout="feature/demo\n")],
        }
    )

    response = git.create_branch(
        build_record(tmp_path),
        GitBranchCreateRequest(name="feature/demo", confirm=True),
    )

    assert response.branch == "feature/demo"
    assert response.current == "feature/demo"
    assert ("switch", "-c", "feature/demo") in git.calls


def test_project_git_commit_stages_paths_and_commits(tmp_path: Path) -> None:
    git = FakeProjectGitAutomation(
        {
            ("rev-parse", "--is-inside-work-tree"): [
                result(stdout="true\n"),
                result(stdout="true\n"),
            ],
            ("add", "--", "README.md"): [result()],
            ("diff", "--cached", "--quiet"): [result(returncode=1)],
            ("commit", "-m", "docs: update readme"): [result(stdout="[main abc123] ok\n")],
            ("rev-parse", "--short", "HEAD"): [
                result(stdout="abc123\n"),
                result(stdout="abc123\n"),
            ],
            ("branch", "--show-current"): [result(stdout="main\n")],
            ("status", "--porcelain=v1"): [result(stdout="")],
        }
    )

    response = git.commit(
        build_record(tmp_path),
        GitCommitRequest(
            message="docs: update readme",
            paths=["README.md"],
            confirm=True,
        ),
    )

    assert response.committed is True
    assert response.commit == "abc123"
    assert response.status.dirty is False
    assert ("add", "--", "README.md") in git.calls
    assert ("commit", "-m", "docs: update readme") in git.calls


def test_project_git_commit_rejects_paths_with_stage_all(tmp_path: Path) -> None:
    git = FakeProjectGitAutomation({})

    with pytest.raises(GitAutomationError, match="either stage_all or paths"):
        git.commit(
            build_record(tmp_path),
            GitCommitRequest(
                message="docs: update readme",
                paths=["README.md"],
                stage_all=True,
                confirm=True,
            ),
        )
