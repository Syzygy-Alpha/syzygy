# NERV Quick Actions

## Context

NERV already exposed module cards, runtime state, and launch actions, but the
user still needed to open endpoints manually to inspect common module data.

The next useful refinement was to turn a small set of known operational reads
into explicit quick actions that run inside the dashboard itself.

## Created

- Added a quick action catalog for known module surfaces.
- Added a NERV action executor for catalog-declared HTTP actions.
- Added `POST /api/surfaces/{name}/actions/{action_name}/run`.
- Added an inline operations console to display action results in the dashboard.
- Added tests for the action executor, API route, and catalog coverage.
- Added Sprint 002 documentation.

## What It Does Now

NERV can execute a curated set of safe module reads directly from the dashboard,
including examples such as:

- Forge current project and outbox summary
- Observatory health summaries and polling state
- Mycelium local node and peer list
- Foundation health and version

This keeps the operational center lightweight while reducing repetitive manual
endpoint work.

## Scope Boundary

This does not turn NERV into a generic API client, write console, or persistent
operations history. Quick actions remain explicit, catalog-driven, and local.

## Validation

- `git diff --check` passed.
- `python -m pytest --version` failed because `python.exe` is not starting in
  the current session.
- `py -3 -m pytest --version` also failed because the configured Python 3.11
  runtime could not be created in the current session.
