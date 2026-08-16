# Observatory Health Trends

## Context

Observatory had local health observations, latest-state summaries, and optional
Foundation module polling. The next useful local-first capability was to expose
simple trend information from the SQLite history already being collected.

## Created

- Added health trend models for stored observations.
- Added trend aggregation by service/module.
- Added `GET /health-observations/trends` with optional `name` filtering.
- Added Observatory capability metadata for health trends.
- Added tests for trend aggregation and API output.
- Updated Observatory and project documentation.

## What It Does Now

Observatory can return one trend per service/module with:

- total observations;
- counts by status;
- first and latest observation timestamps;
- latest status;
- status change count.

## Scope Boundary

This does not add graph rendering, dashboards, alerts, metrics scraping, or
distributed telemetry. It is a compact read model over existing local
observations.

## Validation

- `python -m ruff check .` passed.
- `python -m mypy src tests` passed.
- `python -m pytest --basetemp .pytest-tmp -o cache_dir=.tmp/pytest_cache`
  passed with 18 tests.
- Pytest emitted a Windows cache warning, but the suite completed successfully.
