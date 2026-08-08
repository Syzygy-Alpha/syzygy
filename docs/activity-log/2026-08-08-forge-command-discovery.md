# 2026-08-08 - Forge Command Discovery

## Context

Forge can create a project with a `syzygy.project.toml` manifest. The next safe
step is reading declared project commands without executing them.

## Created

- Project manifest reader.
- `GET /projects/{name}/commands` endpoint.
- Tests for valid manifests, missing manifests, invalid command values, and API
  behavior.
- Forge documentation for command discovery.

## What It Does Now

Forge can read the `[commands]` table from a registered project's
`syzygy.project.toml` and return command names with their configured command
strings.

## Scope Boundary

Forge still does not execute commands. This increment is read-only and prepares
the contract for future safe command execution.

## Validation

Validated with:

```text
ruff check .
mypy src tests
pytest
```

Result: 24 tests passed.
