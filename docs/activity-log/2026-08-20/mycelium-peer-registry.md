# Mycelium Peer Registry

## Context

Mycelium already had a local Hypha node descriptor, but it still lacked a
stable local contract for representing other known nodes before attempting any
real discovery protocol.

The roadmap explicitly called for a local peer registry before network
discovery. This increment adds that registry without pulling Mycelium into
premature sync or transport complexity.

## Created

- Added SQLite-backed Mycelium database and migrations.
- Added a local peer registry with register, list, and get operations.
- Added `POST /peers`, `GET /peers`, and `GET /peers/{node_id}`.
- Added Mycelium peer registry capability metadata.
- Added tests for database initialization, peer registry behavior, config
  defaults, and API behavior.
- Added ADR-002 for the local peer registry decision.
- Updated Mycelium and project documentation.

## What It Does Now

Mycelium can store a durable local record of manually known peers, including:

- node identity
- address
- agent
- status
- source
- capabilities

This gives the mesh module a stable local-first registry contract before any
automatic discovery or synchronization is introduced.

## Scope Boundary

This does not add peer probing, discovery broadcasts, heartbeats, replication,
backup, or file synchronization. It is only a local registry for explicitly
known peers.

## Validation

- `git diff --check` passed.
- Python-based validation could not run because the local Python launcher/runtime
  available in this session is not starting successfully.
