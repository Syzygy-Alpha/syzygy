from pydantic import BaseModel


class TemplateFile(BaseModel):
    path: str
    content: str


class ProjectTemplate(BaseModel):
    name: str
    description: str
    files: list[TemplateFile]


def list_project_templates() -> list[ProjectTemplate]:
    return sorted(PROJECT_TEMPLATES.values(), key=lambda template: template.name)


def get_project_template(name: str) -> ProjectTemplate | None:
    return PROJECT_TEMPLATES.get(name)


PYTHON_CLI_TEMPLATE = ProjectTemplate(
    name="python-cli",
    description="Minimal Python command-line project.",
    files=[
        TemplateFile(
            path="README.md",
            content="""# {{ project_name }}

Minimal Python command-line project created by SYZYGY Forge.

## Usage

```bash
python -m {{ package_name }}
```
""",
        ),
        TemplateFile(
            path="pyproject.toml",
            content="""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{{ project_name }}"
version = "0.1.0"
description = "A local project created by SYZYGY Forge."
readme = "README.md"
requires-python = ">=3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
""",
        ),
        TemplateFile(
            path="src/{{ package_name }}/__init__.py",
            content='"""{{ project_name }} package."""\n',
        ),
        TemplateFile(
            path="src/{{ package_name }}/__main__.py",
            content="""from {{ package_name }}.main import main


if __name__ == "__main__":
    main()
""",
        ),
        TemplateFile(
            path="src/{{ package_name }}/main.py",
            content="""def main() -> None:
    print("{{ project_name }} is alive")
""",
        ),
        TemplateFile(
            path="tests/test_smoke.py",
            content="""from {{ package_name }}.main import main


def test_main_runs(capsys):
    main()

    assert "{{ project_name }} is alive" in capsys.readouterr().out
""",
        ),
        TemplateFile(
            path="syzygy.project.toml",
            content="""name = "{{ project_name }}"
template = "python-cli"

[commands]
test = "python -m pytest"
lint = "python -m ruff check ."
run = "python -m {{ package_name }}"
""",
        ),
    ],
)


PROJECT_TEMPLATES = {
    PYTHON_CLI_TEMPLATE.name: PYTHON_CLI_TEMPLATE,
}
