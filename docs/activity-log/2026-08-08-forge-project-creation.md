# 2026-08-08 - Forge Project Creation

## Context

Forge could register and inspect existing projects. The next concrete step was
to create a small local project from a known template while staying inside the
configured workspace root.

## Created

- Built-in `python-cli` project template.
- Project template listing endpoints.
- `POST /projects/create` endpoint.
- Project creator service that writes files locally and registers the project.
- Tests for project creation and API behavior.

## What It Does Now

Forge can create a minimal Python CLI project containing:

- `README.md`
- `pyproject.toml`
- package source files
- smoke test
- `syzygy.project.toml`

## Scope Boundary

Forge still does not install dependencies, run commands, create commits, build
artifacts, deploy, or push to remotes. Git initialization is opt-in and only
runs `git init` locally.

## Validation

Validated with:

```text
ruff check .
mypy src tests
pytest
```

Result: 20 tests passed.
