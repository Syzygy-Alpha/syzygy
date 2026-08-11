import re
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field

from syzygy_forge.project_registry import ProjectRecord

BRANCH_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")


class GitAutomationError(ValueError):
    pass


class GitCommandResult(BaseModel):
    returncode: int
    stdout: str
    stderr: str


class GitFileStatus(BaseModel):
    path: str
    index: str
    worktree: str


class ProjectGitStatus(BaseModel):
    is_repository: bool
    branch: str | None = None
    commit: str | None = None
    dirty: bool = False
    files: list[GitFileStatus] = Field(default_factory=list)


class GitBranch(BaseModel):
    name: str
    current: bool = False


class GitBranchListResult(BaseModel):
    current: str | None = None
    branches: list[GitBranch] = Field(default_factory=list)


class GitBranchCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    checkout: bool = Field(default=True)
    confirm: bool = Field(default=False)


class GitBranchSwitchRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    confirm: bool = Field(default=False)


class GitBranchOperationResult(BaseModel):
    branch: str
    current: str | None
    stdout: str = ""
    stderr: str = ""


class GitCommitRequest(BaseModel):
    message: str = Field(min_length=1, max_length=200)
    paths: list[str] = Field(default_factory=list)
    stage_all: bool = Field(default=False)
    confirm: bool = Field(default=False)


class GitCommitResult(BaseModel):
    committed: bool
    commit: str | None
    stdout: str
    stderr: str
    status: ProjectGitStatus


class ProjectGitAutomation:
    def status(self, record: ProjectRecord) -> ProjectGitStatus:
        path = Path(record.path).resolve()
        if not self._is_repository(path):
            return ProjectGitStatus(is_repository=False)

        branch = self._branch(path)
        commit = self._commit(path)
        files = self._status_files(path)
        return ProjectGitStatus(
            is_repository=True,
            branch=branch,
            commit=commit,
            dirty=bool(files),
            files=files,
        )

    def branches(self, record: ProjectRecord) -> GitBranchListResult:
        path = self._repository_path(record)
        current = self._branch(path)
        result = self._git(path, "branch", "--list", "--format=%(refname:short)")
        if result.returncode != 0:
            msg = result.stderr.strip() or "Unable to list Git branches"
            raise GitAutomationError(msg)
        branches = [
            GitBranch(name=name, current=name == current)
            for name in result.stdout.splitlines()
            if name.strip()
        ]
        return GitBranchListResult(current=current, branches=branches)

    def create_branch(
        self,
        record: ProjectRecord,
        request: GitBranchCreateRequest,
    ) -> GitBranchOperationResult:
        if not request.confirm:
            msg = "Git branch creation requires confirm=true"
            raise GitAutomationError(msg)
        branch = self._validate_branch_name(request.name)
        path = self._repository_path(record)
        args = ("switch", "-c", branch) if request.checkout else ("branch", branch)
        result = self._git(path, *args)
        if result.returncode != 0:
            msg = result.stderr.strip() or result.stdout.strip() or "Git branch creation failed"
            raise GitAutomationError(msg)
        return GitBranchOperationResult(
            branch=branch,
            current=self._branch(path),
            stdout=result.stdout,
            stderr=result.stderr,
        )

    def switch_branch(
        self,
        record: ProjectRecord,
        request: GitBranchSwitchRequest,
    ) -> GitBranchOperationResult:
        if not request.confirm:
            msg = "Git branch switch requires confirm=true"
            raise GitAutomationError(msg)
        branch = self._validate_branch_name(request.name)
        path = self._repository_path(record)
        result = self._git(path, "switch", branch)
        if result.returncode != 0:
            msg = result.stderr.strip() or result.stdout.strip() or "Git branch switch failed"
            raise GitAutomationError(msg)
        return GitBranchOperationResult(
            branch=branch,
            current=self._branch(path),
            stdout=result.stdout,
            stderr=result.stderr,
        )

    def commit(self, record: ProjectRecord, request: GitCommitRequest) -> GitCommitResult:
        if not request.confirm:
            msg = "Git commit requires confirm=true"
            raise GitAutomationError(msg)
        message = request.message.strip()
        if not message:
            msg = "Git commit message cannot be empty"
            raise GitAutomationError(msg)
        if request.stage_all and request.paths:
            msg = "Use either stage_all or paths, not both"
            raise GitAutomationError(msg)

        path = self._repository_path(record)
        if request.stage_all:
            self._run_or_raise(path, "add", "-A")
        elif request.paths:
            self._run_or_raise(path, "add", "--", *self._validate_paths(request.paths))

        staged = self._git(path, "diff", "--cached", "--quiet")
        if staged.returncode == 0:
            msg = "No staged changes to commit"
            raise GitAutomationError(msg)
        if staged.returncode not in {0, 1}:
            msg = staged.stderr.strip() or "Unable to inspect staged changes"
            raise GitAutomationError(msg)

        result = self._git(path, "commit", "-m", message)
        if result.returncode != 0:
            msg = result.stderr.strip() or result.stdout.strip() or "Git commit failed"
            raise GitAutomationError(msg)
        return GitCommitResult(
            committed=True,
            commit=self._commit(path),
            stdout=result.stdout,
            stderr=result.stderr,
            status=self.status(record),
        )

    def _repository_path(self, record: ProjectRecord) -> Path:
        path = Path(record.path).resolve()
        if not self._is_repository(path):
            msg = f"Project is not a Git repository: {record.name}"
            raise GitAutomationError(msg)
        return path

    def _is_repository(self, path: Path) -> bool:
        result = self._git(path, "rev-parse", "--is-inside-work-tree")
        return result.returncode == 0 and result.stdout.strip() == "true"

    def _branch(self, path: Path) -> str | None:
        result = self._git(path, "branch", "--show-current")
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        fallback = self._git(path, "rev-parse", "--abbrev-ref", "HEAD")
        if fallback.returncode == 0 and fallback.stdout.strip() != "HEAD":
            return fallback.stdout.strip()
        return None

    def _commit(self, path: Path) -> str | None:
        result = self._git(path, "rev-parse", "--short", "HEAD")
        if result.returncode != 0:
            return None
        return result.stdout.strip() or None

    def _status_files(self, path: Path) -> list[GitFileStatus]:
        result = self._git(path, "status", "--porcelain=v1")
        if result.returncode != 0:
            return []
        files = []
        for line in result.stdout.splitlines():
            if len(line) < 4:
                continue
            files.append(
                GitFileStatus(
                    index=line[0],
                    worktree=line[1],
                    path=line[3:],
                )
            )
        return files

    def _validate_branch_name(self, value: str) -> str:
        branch = value.strip()
        if (
            not BRANCH_NAME_PATTERN.fullmatch(branch)
            or ".." in branch
            or branch.endswith("/")
            or branch.endswith(".lock")
        ):
            msg = "Git branch name is invalid"
            raise GitAutomationError(msg)
        return branch

    def _validate_paths(self, paths: list[str]) -> list[str]:
        validated = []
        for value in paths:
            path = Path(value)
            if path.is_absolute() or ".." in path.parts or not value.strip():
                msg = f"Git path is invalid: {value}"
                raise GitAutomationError(msg)
            validated.append(value)
        return validated

    def _run_or_raise(self, path: Path, *args: str) -> GitCommandResult:
        result = self._git(path, *args)
        if result.returncode != 0:
            msg = result.stderr.strip() or result.stdout.strip() or "Git command failed"
            raise GitAutomationError(msg)
        return result

    def _git(self, cwd: Path, *args: str) -> GitCommandResult:
        try:
            completed = subprocess.run(
                ["git", *args],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return GitCommandResult(returncode=1, stdout="", stderr=str(exc))
        return GitCommandResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
