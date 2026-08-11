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


PYTHON_PACKAGE_TEMPLATE = ProjectTemplate(
    name="python-package",
    description="Minimal Python package with tests and lint commands.",
    files=[
        TemplateFile(
            path="README.md",
            content="""# {{ project_name }}

Minimal Python package created by SYZYGY Forge.

## Development

```bash
python -m pytest
python -m ruff check .
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
description = "A local Python package created by SYZYGY Forge."
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
            content="""from {{ package_name }}.core import describe

__all__ = ["describe"]
""",
        ),
        TemplateFile(
            path="src/{{ package_name }}/core.py",
            content="""def describe() -> str:
    return "{{ project_name }} package"
""",
        ),
        TemplateFile(
            path="tests/test_core.py",
            content="""from {{ package_name }} import describe


def test_describe() -> None:
    assert describe() == "{{ project_name }} package"
""",
        ),
        TemplateFile(
            path="syzygy.project.toml",
            content="""name = "{{ project_name }}"
template = "python-package"

[commands]
test = "python -m pytest"
lint = "python -m ruff check ."
""",
        ),
    ],
)


STATIC_SITE_TEMPLATE = ProjectTemplate(
    name="static-site",
    description="Minimal static HTML, CSS, and JavaScript project.",
    files=[
        TemplateFile(
            path="README.md",
            content="""# {{ project_name }}

Minimal static site created by SYZYGY Forge.

## Local Preview

```bash
python -m http.server 8000
```

Then open `http://127.0.0.1:8000`.
""",
        ),
        TemplateFile(
            path="index.html",
            content="""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ project_name }}</title>
    <link rel="stylesheet" href="styles.css">
  </head>
  <body>
    <main>
      <h1>{{ project_name }}</h1>
      <p>Static site created by SYZYGY Forge.</p>
      <button id="status-button" type="button">Check status</button>
      <p id="status">Ready.</p>
    </main>
    <script src="app.js"></script>
  </body>
</html>
""",
        ),
        TemplateFile(
            path="styles.css",
            content="""body {
  margin: 0;
  min-height: 100vh;
  display: grid;
  place-items: center;
  font-family: Arial, sans-serif;
  background: #f5f7fa;
  color: #17202a;
}

main {
  width: min(720px, calc(100% - 32px));
}

button {
  padding: 8px 12px;
}
""",
        ),
        TemplateFile(
            path="app.js",
            content="""const statusElement = document.querySelector("#status");
const statusButton = document.querySelector("#status-button");

statusButton?.addEventListener("click", () => {
  statusElement.textContent = "{{ project_name }} is alive.";
});
""",
        ),
        TemplateFile(
            path="syzygy.project.toml",
            content="""name = "{{ project_name }}"
template = "static-site"

[commands]
serve = "python -m http.server 8000"
""",
        ),
    ],
)


PROJECT_TEMPLATES = {
    PYTHON_CLI_TEMPLATE.name: PYTHON_CLI_TEMPLATE,
    PYTHON_PACKAGE_TEMPLATE.name: PYTHON_PACKAGE_TEMPLATE,
    STATIC_SITE_TEMPLATE.name: STATIC_SITE_TEMPLATE,
}
