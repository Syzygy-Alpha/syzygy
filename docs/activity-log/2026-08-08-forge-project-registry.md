# 2026-08-08 - Forge Project Registry

## Context

Forge could inspect one configured workspace root, but it did not yet know which
local projects it should track.

## Created

- Forge SQLite database configuration.
- Forge schema migration runner.
- Persistent local project registry.
- `POST /projects`, `GET /projects`, and `GET /projects/{name}` endpoints.
- Tests for persistence behavior and API behavior.
- ADR for the Forge local project registry decision.

## What It Does Now

Forge can register an existing local project path under a stable name, list
registered projects, and return a stored record with a fresh read-only
inspection.

## Scope Boundary

Forge still does not mutate repositories. It does not commit, build, deploy, or
run automation.

## Validation

Validated with:

```text
ruff check .
mypy src tests
pytest
```

Result: 13 tests passed.
