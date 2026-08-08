# 2026-08-08 - Forge Project Inspection

## Context

Forge exists as a module and can register itself with Foundation. The next
concrete engineering capability is read-only local project inspection.

## Created

- Project inspection model.
- Git status inspector using read-only `git` commands.
- `GET /projects/current` endpoint.
- Tests for missing paths, non-Git directories, Git status parsing, and the API
  endpoint.
- Forge documentation for project inspection.

## What It Does Now

Forge can inspect the configured workspace root and report:

- resolved path
- whether the path exists
- whether it is inside a Git repository
- current branch
- short commit
- dirty state

## Scope Boundary

Forge still does not mutate repositories. It does not commit, build, deploy,
create templates, or run automation. This increment is read-only.

## Validation

Validated with:

```text
pytest
ruff check .
mypy src tests
```

