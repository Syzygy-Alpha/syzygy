import re
import shlex
from pathlib import Path

from pydantic import BaseModel

from syzygy_forge.project_manifest import ProjectCommand, ProjectCommandSet
from syzygy_forge.project_registry import ProjectRecord

COMMAND_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
ALLOWED_EXECUTABLES = frozenset({"py", "python", "python3", "pytest", "ruff"})
SHELL_CONTROL_TOKENS = frozenset(
    {
        "&",
        "&&",
        "|",
        "||",
        ";",
        "<",
        ">",
        ">>",
        "$(",
        "`",
    }
)


class ProjectCommandPlan(BaseModel):
    project: str
    command_name: str
    command: str
    cwd: str
    argv: list[str]
    allowed: bool
    reason: str


class ProjectCommandPlanner:
    def plan(
        self,
        record: ProjectRecord,
        command_set: ProjectCommandSet,
        command_name: str,
    ) -> ProjectCommandPlan:
        command = self._find_command(command_set, command_name)
        if command is None:
            return self._blocked(record, command_name, "", [], "Project command not found")

        argv = self._split(command.command)
        reason = self._reason(command.name, command.command, argv)
        return ProjectCommandPlan(
            project=record.name,
            command_name=command.name,
            command=command.command,
            cwd=str(Path(record.path).resolve()),
            argv=argv,
            allowed=reason == "allowed",
            reason=reason,
        )

    def _find_command(
        self,
        command_set: ProjectCommandSet,
        command_name: str,
    ) -> ProjectCommand | None:
        for command in command_set.commands:
            if command.name == command_name:
                return command
        return None

    def _split(self, command: str) -> list[str]:
        try:
            return shlex.split(command)
        except ValueError:
            return []

    def _reason(self, command_name: str, command: str, argv: list[str]) -> str:
        if not COMMAND_NAME_PATTERN.fullmatch(command_name):
            return "command name is invalid"
        if not command.strip():
            return "command is empty"
        if not argv:
            return "command cannot be parsed"
        if "\n" in command or "\r" in command:
            return "command contains a newline"
        if any(token in command for token in SHELL_CONTROL_TOKENS):
            return "command contains shell control syntax"
        executable = Path(argv[0]).name.lower()
        if executable not in ALLOWED_EXECUTABLES:
            return "command executable is not allowed"
        return "allowed"

    def _blocked(
        self,
        record: ProjectRecord,
        command_name: str,
        command: str,
        argv: list[str],
        reason: str,
    ) -> ProjectCommandPlan:
        return ProjectCommandPlan(
            project=record.name,
            command_name=command_name,
            command=command,
            cwd=str(Path(record.path).resolve()),
            argv=argv,
            allowed=False,
            reason=reason,
        )
