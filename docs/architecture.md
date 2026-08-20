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

The functional modules are:

- Foundation v0.1
- Forge v0.1
- Mycelium v0.1
- Observatory v0.1
- NERV v0.1

Foundation currently provides:

- FastAPI HTTP API
- typed configuration
- health and version endpoints
- SQLite persistence abstraction
- JWT authentication
- EventBus interface with NATS adapter
- scheduler abstraction
- module lifecycle descriptor

Forge currently provides:

- project registry and creation
- project command discovery, planning, execution, and history
- command lifecycle event contracts and local outbox
- opt-in event publishing and manual requeue
- local Git status, branch, and commit workflows

Mycelium currently provides:

- local Hypha node descriptor
- local peer registry for manually known nodes
- health, version, and capabilities endpoints
- optional Foundation module registration

Observatory currently provides:

- local health observation storage
- health observation listing and filtering
- health summary by status and latest service/module state
- health trend summaries from stored observations
- manual ingestion of Foundation module health through the module registry API
- optional scheduled polling of Foundation module health

NERV currently provides:

- local operational dashboard
- local surface catalog for known SYZYGY modules
- local start and stop actions for known module servers
- catalog-defined quick actions for common module reads
- live endpoint reachability checks
- optional Foundation registry visibility

## Deferred Capabilities

The architecture explicitly defers:

- Mycelium device discovery, distributed sync, replication, and backup
- Coppermind knowledge/RAG
- MAGI agents
- deeper NERV orchestration for devices, containers, and agents
- Tungsten vault/security stack
- full Observatory dashboards, metrics, tracing, and alerting
- Bastion labs
