# NERV Catalog Import Fix

## Context

After the Sprint 002 quick action catalog was installed in a local virtual
environment, starting NERV with Uvicorn failed while importing
`syzygy_nerv.catalog`.

`SurfaceCatalog` has a public `list()` method. On Python 3.11, annotations in
the class body were being evaluated while that method already shadowed the
built-in `list` type. The later `list[SurfaceEntry]` annotation therefore
raised `TypeError: 'function' object is not subscriptable`.

## Fixed

- Enabled postponed annotation evaluation in the NERV surface catalog.
- Preserved the existing public `SurfaceCatalog.list()` contract and all
  catalog action definitions.

## Validation

- The existing catalog test imports and instantiates `SurfaceCatalog`, covering
  the failing application import path.
- `git diff --check` passed.
- The local `.venv` could not run pytest, Ruff, or mypy because it was created
  from a Windows Store Python base executable that cannot create a process in
  this session. This is an environment issue, not a test failure.
