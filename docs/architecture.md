# SYZYGY Architecture

SYZYGY is organized as a modular platform. Foundation is the first implementation
and provides the shared core contracts used by future modules.

## Conceptual Module Relationship

```text
                         ELRIC
                           |
                           v
                          NERV
                           |
                           v
                       FOUNDATION
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      MYCELIUM          FORGE         OBSERVATORY
          |                                 |
          v                                 |
      TUNGSTEN <---------------------------+
          |
          v
      COPPERMIND
          |
          v
         MAGI
          |
          v
       BALANCE
```

This is conceptual. It does not mean every module must call the module below it
directly. Contracts and events should be preferred where they reduce coupling.

## Dependency Rules

- Foundation should not depend on future modules.
- Future modules should depend on Foundation contracts rather than internal
  implementation details.
- Avoid circular dependencies.
- Prefer explicit contracts: events, APIs, messages, schemas, and interfaces.

## Current Implementation

The only functional module is:

- Foundation v0.1

Foundation currently provides:

- FastAPI HTTP API
- typed configuration
- health and version endpoints
- SQLite persistence abstraction
- JWT authentication
- EventBus interface with NATS adapter
- scheduler abstraction
- module lifecycle descriptor

## Deferred Capabilities

The architecture explicitly defers:

- Mycelium distributed sync
- Coppermind knowledge/RAG
- MAGI agents
- NERV UI
- Tungsten vault/security stack
- Forge automation
- Bastion labs

