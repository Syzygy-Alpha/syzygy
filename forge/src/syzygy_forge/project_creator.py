import re
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field

from syzygy_forge.project_registry import ProjectRecord, ProjectRegistry
from syzygy_forge.project_templates import ProjectTemplate, get_project_template

PROJECT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


class ProjectCreationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    template: str = Field(default="python-cli", min_length=1)
    initialize_git: bool = Field(default=False)


class ProjectCreationResult(BaseModel):
    record: ProjectRecord
    template: str
    files: list[str]
    git_initialized: bool = False
    git_error: str | None = None


class ProjectCreationError(ValueError):
    pass


class ProjectCreator:
    def __init__(self, workspace_root: Path, project_registry: ProjectRegistry) -> None:
        self.workspace_root = workspace_root
        self.project_registry = project_registry

    def create(self, request: ProjectCreationRequest) -> ProjectCreationResult:
        if not PROJECT_NAME_PATTERN.fullmatch(request.name):
            msg = "Project name must use only letters, numbers, underscores, or hyphens"
            raise ProjectCreationError(msg)

        template = get_project_template(request.template)
        if template is None:
            msg = f"Unknown project template: {request.template}"
            raise ProjectCreationError(msg)

        workspace_root = self.workspace_root.resolve()
        target_path = (workspace_root / request.name).resolve()
        self._ensure_target_inside_workspace(workspace_root, target_path)
        if target_path.exists():
            msg = f"Project path already exists: {target_path}"
            raise ProjectCreationError(msg)

        rendered_files = self._render_template(template, request.name)
        target_path.mkdir(parents=True)
        for relative_path, content in rendered_files:
            file_path = target_path / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")

        git_initialized = False
        git_error = None
        if request.initialize_git:
            git_initialized, git_error = self._initialize_git(target_path)

        record = self.project_registry.register(target_path, request.name)
        return ProjectCreationResult(
            record=record,
            template=template.name,
            files=[relative_path.as_posix() for relative_path, _ in rendered_files],
            git_initialized=git_initialized,
            git_error=git_error,
        )

    def _render_template(
        self,
        template: ProjectTemplate,
        project_name: str,
    ) -> list[tuple[Path, str]]:
        package_name = self._package_name(project_name)
        replacements = {
            "{{ project_name }}": project_name,
            "{{ package_name }}": package_name,
        }
        rendered_files = []
        for template_file in template.files:
            path = template_file.path
            content = template_file.content
            for token, value in replacements.items():
                path = path.replace(token, value)
                content = content.replace(token, value)
            rendered_files.append((Path(path), content))
        return rendered_files

    def _package_name(self, project_name: str) -> str:
        package_name = project_name.replace("-", "_").lower()
        if package_name[0].isdigit():
            package_name = f"project_{package_name}"
        return package_name

    def _ensure_target_inside_workspace(self, workspace_root: Path, target_path: Path) -> None:
        try:
            target_path.relative_to(workspace_root)
        except ValueError as exc:
            msg = "Project target must stay inside the configured workspace root"
            raise ProjectCreationError(msg) from exc

    def _initialize_git(self, target_path: Path) -> tuple[bool, str | None]:
        try:
            completed = subprocess.run(
                ["git", "init"],
                cwd=target_path,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return False, str(exc)
        if completed.returncode != 0:
            return False, completed.stderr.strip() or completed.stdout.strip()
        return True, None
