# ADR-001 - Forge Local Project Registry

## Context

Forge is responsible for projects, Git workflows, builds, deploys, templates,
containers, CI/CD, and programming automation. Before adding build or commit
automation, Forge needs a stable local record of projects it knows about.

## Decision

Forge will maintain its own SQLite-backed local project registry.

The first registry stores:

- project name
- resolved local path
- creation timestamp
- update timestamp

The registry is module-owned and does not depend on Foundation internals.
Foundation remains responsible for module lifecycle and discovery, not for
storing Forge project records.

## Alternatives

- Store project records only in memory.
- Store project records inside Foundation.
- Use a JSON file.

## Consequences

- Forge can restart and retain known projects.
- The implementation stays local-first and self-contained.
- Future build and commit automation can depend on explicit project records.
- SQLite schema changes must be handled through Forge migrations.

## Status

Accepted
