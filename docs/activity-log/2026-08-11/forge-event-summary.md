# 2026-08-11 - Forge Event Summary

## Context

Forge could store, publish, fail, and requeue outbox events, but operators still
had to inspect the full event list to understand local delivery health.

## Created

- `GET /events/outbox/summary` endpoint.
- Outbox summary model with status counts, attempts, delivery status, oldest
  pending event, and latest failed event.
- Forge capability `event_outbox_summary`.
- Unit and API tests for empty, pending, failed, and published states.

## What It Does Now

Forge can report local outbox delivery health without publishing events or
mutating state. This gives a compact view for future NERV or Observatory
consumers while keeping the data local and SQLite-backed.

## Scope Boundary

This does not implement scheduled retry, dashboards, metrics export, or
cross-module observability. Those remain future work.

## Validation

Validated with:

```text
ruff check .
mypy src tests
pytest
```

Result: 60 tests passed.
