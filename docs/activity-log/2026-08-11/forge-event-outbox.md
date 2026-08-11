# 2026-08-11 - Forge Event Outbox

## Context

Forge had command lifecycle event contracts but no local routing path for those
events. Publishing directly to an external transport would add infrastructure
coupling too early.

## Created

- SQLite migration for a local Forge event outbox.
- `ForgeEventOutbox` repository.
- `GET /events/outbox` endpoint.
- Automatic outbox enqueue of `CommandRunStarted` and `CommandRunCompleted`
  after confirmed command execution.
- Tests for outbox persistence, status filtering, and API integration.

## What It Does Now

Forge records command lifecycle events locally as pending outbox entries. The
payloads omit stdout and stderr.

## Scope Boundary

Forge still does not publish events to NATS or Foundation directly. The outbox
is the durable local boundary for future delivery.

## Validation

Validated with:

```text
ruff check .
mypy src tests
pytest
```

Result: 39 tests passed.
