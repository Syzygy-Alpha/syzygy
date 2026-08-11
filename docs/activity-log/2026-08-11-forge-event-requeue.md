# 2026-08-11 - Forge Event Requeue

## Context

Forge could publish pending outbox events and mark delivery failures as
`failed`, but there was no explicit recovery path for retrying those failed
records.

## Created

- Manual requeue operations for failed outbox records.
- `POST /events/outbox/{record_id}/requeue` endpoint.
- `POST /events/outbox/requeue-failed` endpoint.
- Outbox repository methods for listing and requeuing failed events.
- Tests for unit behavior, API confirmation, missing records, invalid status,
  and bulk requeue.

## What It Does Now

Forge can move failed events back to `pending` only through explicit confirmed
requests. The operation preserves `attempts` and clears `last_error` so the
event can be published again by the existing publisher endpoint.

## Scope Boundary

Forge still does not retry failed events automatically. Retry scheduling and
delivery health summaries remain future operational work.

## Validation

Validated with:

```text
ruff check .
mypy src tests
pytest
```

Result: 55 tests passed.
