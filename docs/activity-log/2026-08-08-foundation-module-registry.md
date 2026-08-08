# 2026-08-08 - Foundation Module Registry API

## Context

Foundation had an in-memory module registry. That was enough to expose the
Foundation contract, but future modules need a concrete and persistent way to
register themselves and report lifecycle state.

## Created

- SQLite migration for `foundation_modules`.
- Persistent `ModuleRegistry`.
- Authenticated module registration and lookup endpoints.
- Authenticated module status and health update endpoints.
- Module lifecycle event publication from registry operations.
- Unit and integration tests for module persistence and API behavior.
- Documentation for registry endpoints and event payloads.

## What It Does Now

Foundation can persist module descriptors with:

- name
- version
- status
- health
- capabilities
- dependencies
- last seen timestamp

Future modules can use the registry API as their first integration contract with
Foundation.

## Scope Boundary

This does not implement distributed service discovery, heartbeats, RPC,
Mycelium, Forge, Observatory, or NERV. It only makes Foundation's module
lifecycle contract concrete.

## Validation

Validated with:

```text
pytest
ruff check .
mypy src tests
```

