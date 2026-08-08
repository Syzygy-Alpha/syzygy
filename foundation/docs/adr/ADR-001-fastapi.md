# ADR-001 - FastAPI As Foundation HTTP Framework

## Status

Accepted

## Context

Foundation needs a small internal HTTP API for health, version, authentication,
and future module-facing contracts.

## Decision

Use FastAPI for the Foundation HTTP API.

## Alternatives Considered

- Flask: simple, but less integrated typing and OpenAPI support.
- Django: mature, but too broad for this MVP.

## Consequences

FastAPI keeps the API typed, testable, and small while providing OpenAPI support
without extra framework weight.

