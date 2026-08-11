# 2026-08-07 - Foundation SQLite Migrations

## Context

Foundation v0.1 initialized its SQLite schema directly inside
`Database.initialize`. That works for the first table, but it makes future schema
changes harder to track.

## Created

- Minimal in-code SQLite migration runner.
- `foundation_schema_migrations` tracking table.
- Schema version accessor on the `Database` abstraction.
- Persistence tests that verify migrations are idempotent.
- Development documentation for the migration approach.

## What It Does Now

Database initialization applies versioned migrations once and records each
applied migration. Re-running initialization does not duplicate migration
records.

## Scope Boundary

No external migration framework was added. This does not introduce PostgreSQL,
Alembic, distributed configuration, or module service discovery.

## Validation

Validated with:

```text
pytest
ruff check .
mypy src tests
```

