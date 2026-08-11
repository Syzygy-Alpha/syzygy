# 2026-08-08 - Forge Command Planning

## Context

Forge can discover commands from `syzygy.project.toml`, but command execution
needs an explicit safety contract before anything is run.

## Created

- Command planner for manifest commands.
- Conservative executable allowlist.
- Shell control syntax blocking.
- `GET /projects/{name}/commands/{command_name}/plan` endpoint.
- Tests for allowed commands, blocked shell syntax, blocked executables, missing
  commands, and API integration.

## What It Does Now

Forge can turn a declared command into a plan containing:

- project name
- command name
- original command string
- working directory
- parsed argv
- allow/deny status
- reason

## Scope Boundary

Forge still does not execute commands. The planner prepares the safety boundary
for future explicit, user-approved execution.

## Validation

Validated with:

```text
ruff check .
mypy src tests
pytest
```

Result: 28 tests passed.
