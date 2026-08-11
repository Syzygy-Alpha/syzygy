# Observatory Foundation Ingestion

## Context

After bootstrapping Observatory with local health observations, the next useful
step was to connect it to an existing SYZYGY contract instead of adding a full
metrics stack too early.

Foundation already exposes the authenticated `/modules` registry endpoint, so
Observatory can now read that contract and persist module health snapshots in
its own SQLite-backed health observation store.

## Created

- Added a Foundation module descriptor reader to the Observatory Foundation
  client.
- Added a manual Foundation module ingestion service.
- Added `POST /ingest/foundation/modules` with an explicit `confirm=true`
  guard.
- Added tests for client parsing, ingestion behavior, API confirmation, and the
  advertised Observatory capability.
- Updated Observatory and project documentation.

## What It Does Now

Observatory can:

- authenticate with Foundation;
- read the registered module list from `/modules`;
- convert each module's health into a local health observation;
- expose the ingested state through the existing observation list and summary
  endpoints.

## Scope Boundary

This does not add scheduled polling, dashboards, Prometheus, Grafana, Loki, or
distributed telemetry. It is a manual bridge between the existing Foundation
registry contract and Observatory's local health store.

## Validation

- `python -m ruff check .` passed.
- `python -m mypy src tests` passed.
- `python -m pytest --basetemp .pytest-tmp -o cache_dir=.tmp/pytest_cache`
  passed with 13 tests.
- Pytest emitted a Windows cache warning, but the suite completed successfully.
