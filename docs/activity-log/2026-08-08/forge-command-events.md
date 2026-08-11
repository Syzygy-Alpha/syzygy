# 2026-08-08 - Forge Command Events

## Context

Forge can execute confirmed commands and persist command run history. The next
step is to define command lifecycle event contracts before wiring publication to
the SYZYGY event infrastructure.

## Created

- Forge event envelope.
- `CommandRunStarted` and `CommandRunCompleted` event names.
- Command run event factory.
- Forge event catalog documentation.
- Tests for event subjects, payloads, and omission of stdout/stderr.

## What It Does Now

Forge can build command lifecycle event payloads from persisted command run
records.

## Scope Boundary

Forge does not publish these events yet. This increment only defines and tests
the contract.

## Validation

Validated with:

```text
ruff check .
mypy src tests
pytest
```

Result: 37 tests passed.
