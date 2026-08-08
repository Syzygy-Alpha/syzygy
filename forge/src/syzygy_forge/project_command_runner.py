import subprocess
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from syzygy_forge.project_command_planner import ProjectCommandPlan


class ProjectCommandRunRequest(BaseModel):
    confirm: bool = Field(default=False)
    timeout_seconds: int = Field(default=30, ge=1, le=120)


class ProjectCommandRunResult(BaseModel):
    run_id: int | None = None
    plan: ProjectCommandPlan
    returncode: int | None
    stdout: str
    stderr: str
    timed_out: bool = False
    started_at: datetime
    completed_at: datetime


class ProjectCommandExecutionError(ValueError):
    pass


class ProjectCommandRunner:
    def run(
        self,
        plan: ProjectCommandPlan,
        request: ProjectCommandRunRequest,
    ) -> ProjectCommandRunResult:
        if not request.confirm:
            msg = "Command execution requires confirm=true"
            raise ProjectCommandExecutionError(msg)
        if not plan.allowed:
            msg = f"Command plan is not allowed: {plan.reason}"
            raise ProjectCommandExecutionError(msg)

        started_at = datetime.now(UTC)
        try:
            completed = subprocess.run(
                plan.argv,
                cwd=plan.cwd,
                capture_output=True,
                text=True,
                timeout=request.timeout_seconds,
                check=False,
            )
        except FileNotFoundError as exc:
            completed_at = datetime.now(UTC)
            return ProjectCommandRunResult(
                plan=plan,
                returncode=None,
                stdout="",
                stderr=str(exc),
                started_at=started_at,
                completed_at=completed_at,
            )
        except subprocess.TimeoutExpired as exc:
            completed_at = datetime.now(UTC)
            return ProjectCommandRunResult(
                plan=plan,
                returncode=None,
                stdout=self._output(exc.stdout),
                stderr=self._output(exc.stderr),
                timed_out=True,
                started_at=started_at,
                completed_at=completed_at,
            )

        completed_at = datetime.now(UTC)
        return ProjectCommandRunResult(
            plan=plan,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            started_at=started_at,
            completed_at=completed_at,
        )

    def _output(self, value: str | bytes | None) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode(errors="replace")
        return value
