# Sprint 001 - NERV Command Center Bootstrap

## Context

The project now has working vertical slices in Foundation, Forge, Observatory,
and Mycelium. The next useful ecosystem step is a lightweight operational
surface that reduces manual terminal repetition and gives the user a single
place to access module endpoints and routine launch actions.

The user explicitly wants NERV to become that dashboard, while keeping the
first implementation:

- very light
- visually intentional
- easy to upgrade later
- grounded in documented contracts rather than ad hoc UI work

## Sprint Goal

Bootstrap NERV as a local operational command center for known SYZYGY modules.

## In Scope

- NERV standalone module bootstrap
- local dashboard served by the module itself
- module catalog for known SYZYGY surfaces
- launch and stop actions for supported module servers
- live reachability checks
- optional Foundation registry visibility
- tests, documentation, and activity log

## Out of Scope

- React or Material UI migration
- auth hardening for NERV actions
- container orchestration
- device orchestration
- internal app launchers beyond the module catalog
- persistent operational history
- cross-device control

## Technical Decision

Sprint 001 keeps NERV zero-build on the frontend. The UI is served directly by
FastAPI with static HTML, CSS, and JavaScript so the first release stays local,
fast, and dependency-light.

This is an MVP delivery choice, not a permanent rejection of React. A later
sprint can migrate the UI once the operational contracts are stable enough to
justify a heavier frontend stack.

## Deliverables

- `nerv/` module
- local dashboard UI
- surface catalog
- module supervisor actions
- optional Foundation registry client
- updated project docs

## Exit Criteria

- NERV exposes health, version, and capabilities
- dashboard can be opened locally from `/`
- known modules appear as operational cards
- supported modules can be launched and stopped through NERV APIs
- project docs reflect the new module and the sprint boundary

## Follow-Up Candidates

- internal app surfaces alongside module surfaces
- persisted action history
- richer Forge shortcuts
- registry-backed status transitions
- React migration only if the lightweight contract becomes a bottleneck
