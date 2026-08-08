# ADR-004 - Docker As Development Runtime

## Status

Accepted

## Context

Foundation should run reproducibly with its development dependencies.

## Decision

Provide a Dockerfile and Docker Compose stack for Foundation and NATS.

## Alternatives Considered

- Native-only setup: simpler files, but less reproducible across machines.
- Full orchestration stack: premature for Foundation v0.1.

## Consequences

Developers can run the MVP with `docker compose up --build` while still keeping
local Python development lightweight.

