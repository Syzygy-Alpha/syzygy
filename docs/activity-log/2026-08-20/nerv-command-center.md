# NERV Command Center Bootstrap

## Context

After Foundation, Forge, Observatory, and Mycelium gained minimal operational
spines, the project still lacked a single surface for opening modules, checking
their local state, and reducing repeated terminal work.

The user explicitly repositioned NERV as the next useful module because some
future modules would require heavier dependencies, while NERV could already
deliver immediate value with a local dashboard and launcher.

## Created

- Added the `nerv/` module.
- Added a lightweight FastAPI-served dashboard with static HTML, CSS, and
  JavaScript.
- Added a local surface catalog for Foundation, Forge, Observatory, Mycelium,
  and NERV.
- Added local start and stop actions for known module development servers.
- Added live HTTP reachability probes and optional Foundation registry
  visibility.
- Added tests for config, module descriptor, catalog, Foundation client,
  supervisor, and API behavior.
- Added Sprint 001 documentation and ADR-003 for the zero-build dashboard
  decision.
- Updated project documentation.

## What It Does Now

NERV can act as a lightweight local command center for SYZYGY modules:

- open module endpoints from one place
- launch and stop known local module servers
- show runtime and reachability state
- optionally compare local surfaces with Foundation's module registry

## Scope Boundary

This does not add React, container orchestration, device management,
authentication hardening, or internal app launchers beyond the known module
catalog. It is the first operational spine for NERV.

## Validation

- Code and tests were updated to align with the documented Sprint 001 scope.
- Python-based validation still depends on a working local Python runtime in the
  current session.
