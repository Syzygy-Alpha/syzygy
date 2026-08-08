import subprocess
from pathlib import Path

from pydantic import BaseModel


class GitStatus(BaseModel):
    is_repository: bool
    branch: str | None = None
    commit: str | None = None
    dirty: bool = False


class ProjectInspection(BaseModel):
    path: str
    exists: bool
    git: GitStatus


class GitCommandResult(BaseModel):
    returncode: int
    stdout: str
    stderr: str


class ProjectInspector:
    def inspect(self, path: Path) -> ProjectInspection:
        resolved = path.resolve()
        if not resolved.exists():
            return ProjectInspection(
                path=str(resolved),
                exists=False,
                git=GitStatus(is_repository=False),
            )

        is_repository = self._git(resolved, "rev-parse", "--is-inside-work-tree")
        if is_repository.returncode != 0 or is_repository.stdout.strip() != "true":
            return ProjectInspection(
                path=str(resolved),
                exists=True,
                git=GitStatus(is_repository=False),
            )

        branch = self._git(resolved, "branch", "--show-current").stdout.strip() or None
        commit = self._git(resolved, "rev-parse", "--short", "HEAD").stdout.strip() or None
        dirty = bool(self._git(resolved, "status", "--porcelain").stdout.strip())

        return ProjectInspection(
            path=str(resolved),
            exists=True,
            git=GitStatus(
                is_repository=True,
                branch=branch,
                commit=commit,
                dirty=dirty,
            ),
        )

    def _git(self, cwd: Path, *args: str) -> GitCommandResult:
        try:
            completed = subprocess.run(
                ["git", *args],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return GitCommandResult(returncode=1, stdout="", stderr=str(exc))
        return GitCommandResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
