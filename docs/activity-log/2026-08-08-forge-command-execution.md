# 2026-08-08 - Forge Command Execution

## Context

Forge could plan declared commands safely, but it could not execute even
allowed commands. The next step is explicit, bounded execution with confirmation.

## Created

- Command runner for allowed command plans.
- `POST /projects/{name}/commands/{command_name}/runs` endpoint.
- Confirmation requirement through `confirm=true`.
- Bounded command timeout.
- Tests for confirmed execution, missing confirmation, blocked plans, and API
  execution behavior.

## What It Does Now

Forge can execute a declared command when:

- the command exists in `syzygy.project.toml`;
- the planner marks it as allowed;
- the request explicitly includes `confirm=true`;
- the command completes before the timeout.

Execution uses `subprocess.run` without a shell and runs inside the registered
project path.

## Scope Boundary

Forge still does not commit, push, deploy, or persist command run history. It
captures stdout, stderr, return code, and timeout state for the immediate
response only.

## Validation

Validated with:

```text
ruff check .
mypy src tests
pytest
```

Result: 33 tests passed.
