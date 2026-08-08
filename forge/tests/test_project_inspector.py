from pathlib import Path

from syzygy_forge.project_inspector import GitCommandResult, ProjectInspector


class FakeGitInspector(ProjectInspector):
    def __init__(self, results: dict[tuple[str, ...], GitCommandResult]) -> None:
        self.results = results

    def _git(self, cwd: Path, *args: str) -> GitCommandResult:
        return self.results.get(
            args,
            GitCommandResult(returncode=1, stdout="", stderr="missing fake result"),
        )


def test_project_inspector_reports_missing_path(tmp_path: Path) -> None:
    inspector = ProjectInspector()

    inspection = inspector.inspect(tmp_path / "missing")

    assert inspection.exists is False
    assert inspection.git.is_repository is False


def test_project_inspector_reports_non_git_directory(tmp_path: Path) -> None:
    inspector = FakeGitInspector(
        {
            ("rev-parse", "--is-inside-work-tree"): GitCommandResult(
                returncode=1,
                stdout="",
                stderr="not a repo",
            )
        }
    )

    inspection = inspector.inspect(tmp_path)

    assert inspection.exists is True
    assert inspection.git.is_repository is False


def test_project_inspector_reports_git_status(tmp_path: Path) -> None:
    inspector = FakeGitInspector(
        {
            ("rev-parse", "--is-inside-work-tree"): GitCommandResult(
                returncode=0,
                stdout="true\n",
                stderr="",
            ),
            ("branch", "--show-current"): GitCommandResult(
                returncode=0,
                stdout="main\n",
                stderr="",
            ),
            ("rev-parse", "--short", "HEAD"): GitCommandResult(
                returncode=0,
                stdout="abc123\n",
                stderr="",
            ),
            ("status", "--porcelain"): GitCommandResult(
                returncode=0,
                stdout=" M README.md\n",
                stderr="",
            ),
        }
    )

    inspection = inspector.inspect(tmp_path)

    assert inspection.git.is_repository is True
    assert inspection.git.branch == "main"
    assert inspection.git.commit == "abc123"
    assert inspection.git.dirty is True
