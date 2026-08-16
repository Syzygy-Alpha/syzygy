# Observatory Foundation Polling

## Context

Observatory already had a manual ingestion path for Foundation's `/modules`
registry contract. The next incremental step was to make that ingestion
repeatable without introducing a full observability stack or mandatory
cross-service dependency at startup.

## Created

- Added optional Foundation module polling settings.
- Added a Foundation module poller that reuses the existing ingestion service.
- Added `GET /ingest/foundation/modules/polling` for polling status.
- Added tests for polling defaults, one-shot polling, enabled start/stop, API
  status, and advertised capability.
- Updated Observatory and project documentation.

## What It Does Now

When enabled, Observatory can periodically authenticate with Foundation, read
registered modules from `/modules`, and write local health observations for each
module.

Polling is disabled by default and must be explicitly enabled with:

```text
SYZYGY_OBSERVATORY_FOUNDATION_MODULE_POLLING_ENABLED=true
```

## Scope Boundary

This is not Prometheus, Grafana, Loki, tracing, alerting, or distributed
telemetry. It is a local scheduled bridge between an existing Foundation
contract and Observatory's SQLite-backed health observation store.

## Validation

- `python -m ruff check .` passed.
- `python -m mypy src tests` passed.
- `python -m pytest --basetemp .pytest-tmp -o cache_dir=.tmp/pytest_cache`
  passed with 16 tests.
- Pytest emitted a Windows cache warning, but the suite completed successfully.
