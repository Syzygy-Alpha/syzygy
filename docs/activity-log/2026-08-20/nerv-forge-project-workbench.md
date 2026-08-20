# NERV Forge Project Workbench

## Created

- Added a typed NERV client for Forge projects, declared commands, plans, and
  confirmed command runs.
- Added a Forge project workbench to the NERV dashboard.
- Added plan and run actions for commands from registered project manifests.
- Added a NERV confirmation boundary before execution.
- Added an extra NERV check that prevents a blocked Forge plan from reaching
  Forge's command-run endpoint.
- Added Sprint 003 and ADR-004 documentation.

## Scope Boundary

NERV does not access project files, execute local shell commands, or offer
arbitrary command input. Forge continues to own the project registry, manifest,
allow-list policy, execution, and persisted history.

## Validation

- Automated tests cover the Forge client, blocked plan behavior, and NERV API
  confirmation flow.
- `node --check` passed for the NERV dashboard script.
- `git diff --check` passed.
- The local `.venv` could not run pytest, Ruff, or mypy because its Windows
  Store Python base executable cannot create a process in this session. This is
  an environment limitation, not a test failure.
