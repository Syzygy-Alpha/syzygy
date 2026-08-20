# ADR-002 - Mycelium Local Peer Registry

## Context

Mycelium is the distributed mesh module of SYZYGY, but the project explicitly
defers real discovery, replication, and synchronization until the first local
contracts are stable.

Before attempting any network protocol, Mycelium needs a minimal local record of
known peers that can survive restarts and act as a stable contract for future
manual workflows and discovery experiments.

## Decision

Mycelium will maintain its own SQLite-backed local peer registry.

The first registry stores:

- peer node id
- peer name
- peer address
- peer agent
- peer status
- peer source
- peer capabilities
- creation timestamp
- update timestamp

The registry is module-owned and does not depend on Foundation internals.
Foundation remains responsible for module lifecycle and inter-module discovery,
not for storing Mycelium peer records.

## Alternatives

- Store peers only in memory.
- Store peers inside Foundation.
- Use a JSON file instead of SQLite.

## Consequences

- Mycelium can restart and retain known peers.
- Future discovery and sync work can build on an explicit local peer contract.
- The implementation stays local-first and self-contained.
- SQLite schema changes must be handled through Mycelium migrations.

## Status

Accepted
