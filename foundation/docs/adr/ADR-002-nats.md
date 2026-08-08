# ADR-002 - NATS As EventBus Runtime

## Status

Accepted

## Context

SYZYGY is distributed by design and modules should communicate state changes
through explicit events where appropriate.

## Decision

Use NATS as the development EventBus runtime and keep an internal EventBus
interface so the implementation can evolve.

## Alternatives Considered

- Redis Pub/Sub: simple, but weaker as the long-term event backbone.
- In-process events only: useful for tests, but not enough for distributed nodes.

## Consequences

Foundation can publish and consume events locally through NATS while tests can
use the in-memory adapter.

