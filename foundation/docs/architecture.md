# SYZYGY Foundation Architecture

Foundation is the shared core platform module for SYZYGY. Its MVP exists to
provide small, stable contracts that future modules can depend on without
coupling to implementation details.

## Responsibilities

- Configuration
- Health and version reporting
- Basic authentication
- EventBus abstraction
- Scheduler abstraction
- SQLite persistence
- Internal HTTP API
- Module lifecycle contract

## Explicit Non-Goals

Foundation v0.1 does not implement LLM orchestration, RAG, P2P sync, NERV UI,
advanced Tungsten security, Coppermind indexing, Forge automation, or Bastion
labs. Those modules may integrate later through explicit APIs and events.

## Runtime Shape

```text
FastAPI
  |
  +-- Configuration
  +-- Health
  +-- Authentication
  +-- Module Registry
  +-- Scheduler
  +-- Persistence Adapter
  +-- EventBus Interface
        |
        +-- NATS adapter in development
        +-- In-memory adapter for tests/local fallback
```

## Module Contract

Future modules are represented by:

```json
{
  "name": "mycelium",
  "version": "0.1.0",
  "status": "offline",
  "health": {
    "status": "unknown"
  },
  "capabilities": ["sync", "discovery"],
  "dependencies": ["foundation"]
}
```

Foundation persists this contract through the SQLite-backed registry API.
Network discovery, heartbeats, and distributed service discovery are
intentionally deferred.

## Dependency Direction

Other SYZYGY modules should depend on Foundation contracts. Foundation should not
depend on future modules such as Mycelium, Coppermind, MAGI, NERV, Tungsten, or
Bastion.
