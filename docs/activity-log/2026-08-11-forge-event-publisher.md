# 2026-08-11 - Forge Event Publisher

## Context

Forge already stored command lifecycle events in a local SQLite outbox. The next
useful step was to make those events deliverable without making external
infrastructure mandatory.

## Created

- Opt-in event publisher settings for Forge.
- Publish-state columns for outbox records: `attempts`, `last_error`, and
  `published_at`.
- `EventOutboxPublisher` orchestration service.
- `memory` publisher for local validation.
- `nats` publisher for future SYZYGY event infrastructure integration.
- `POST /events/outbox/publish` endpoint guarded by `confirm=true`.
- Tests for successful publication, failures, disabled API behavior, and API
  integration.

## What It Does Now

Forge can keep events local by default, then publish pending outbox events only
when event publishing is explicitly enabled. Published events are marked as
`published`; delivery failures are marked as `failed` with the error captured.

## Scope Boundary

Forge does not retry failed events automatically yet. It also does not publish
stdout or stderr because command output can contain secrets or sensitive local
data.

## Validation

Validated with:

```text
ruff check .
mypy src tests
pytest
```

Result: 46 tests passed.
