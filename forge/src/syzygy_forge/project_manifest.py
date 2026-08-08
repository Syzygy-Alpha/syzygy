import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from syzygy_forge.project_registry import ProjectRecord


class ProjectCommand(BaseModel):
    name: str
    command: str


class ProjectCommandSet(BaseModel):
    project: str
    manifest_path: str
    commands: list[ProjectCommand]


class ProjectManifestError(ValueError):
    pass


class ProjectManifestReader:
    manifest_filename = "syzygy.project.toml"

    def commands_for(self, record: ProjectRecord) -> ProjectCommandSet:
        manifest_path = Path(record.path) / self.manifest_filename
        payload = self._load_manifest(manifest_path)
        commands_payload = payload.get("commands", {})
        if not isinstance(commands_payload, dict):
            msg = "Project manifest commands must be a table"
            raise ProjectManifestError(msg)

        commands = []
        for name, command in commands_payload.items():
            if not isinstance(name, str) or not isinstance(command, str):
                msg = "Project manifest commands must map names to strings"
                raise ProjectManifestError(msg)
            commands.append(ProjectCommand(name=name, command=command))

        return ProjectCommandSet(
            project=record.name,
            manifest_path=str(manifest_path.resolve()),
            commands=sorted(commands, key=lambda command: command.name),
        )

    def _load_manifest(self, manifest_path: Path) -> dict[str, Any]:
        if not manifest_path.exists():
            msg = f"Project manifest not found: {manifest_path}"
            raise ProjectManifestError(msg)
        try:
            loaded = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            msg = f"Project manifest is not valid TOML: {manifest_path}"
            raise ProjectManifestError(msg) from exc
        return loaded
