# ADR-003 - SQLite As Initial Persistence

## Status

Accepted

## Context

Foundation v0.1 needs persistence that works locally without requiring external
database infrastructure.

## Decision

Use SQLite behind a small persistence abstraction.

## Alternatives Considered

- PostgreSQL: strong default for services, but unnecessary for the first local
  MVP.
- File-only storage: simple, but less suitable for future structured state.

## Consequences

Foundation remains local-first and reproducible. The abstraction keeps future
replacement possible.

