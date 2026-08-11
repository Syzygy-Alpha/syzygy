# 2026-08-08 - Forge Command History

## Context

Forge could execute explicitly confirmed commands and return immediate output,
but those runs were not auditable after the response.

## Created

- SQLite migration for command run history.
- Persistent command run history repository.
- `GET /projects/{name}/command-runs` endpoint.
- Run IDs attached to command execution responses.
- Tests for persistence and API history listing.

## What It Does Now

Forge records metadata for confirmed command executions:

- project
- command name
- command string
- working directory
- allowed status
- planner reason
- return code
- timeout state
- start and completion timestamps

## Scope Boundary

Forge intentionally does not persist stdout or stderr to reduce the chance of
storing secrets or sensitive output in SQLite. The immediate command response
still includes stdout and stderr.

## Validation

Validated with:

```text
ruff check .
mypy src tests
pytest
```

Result: 35 tests passed.
