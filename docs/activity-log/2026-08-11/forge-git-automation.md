# 2026-08-11 - Forge Git Automation

## Context

Forge could inspect whether a project was a Git repository, but it did not yet
provide practical Git workflow endpoints for registered projects.

## Created

- `ProjectGitAutomation` service.
- `GET /projects/{name}/git/status`.
- `GET /projects/{name}/git/branches`.
- `POST /projects/{name}/git/branches`.
- `POST /projects/{name}/git/branches/switch`.
- `POST /projects/{name}/git/commits`.
- Tests for status parsing, branch confirmation, commit staging, API contract,
  and safety validation.
- README and practical usage guide updates.

## What It Does Now

Forge can inspect Git status, list local branches, create or switch branches,
and create local commits with explicit confirmation. Commits can stage specific
relative paths or all changes through `stage_all=true`.

## Scope Boundary

Forge does not push to remotes, manage credentials, resolve merge conflicts, or
perform destructive Git operations.

## Validation

Validated with:

```text
ruff check .
mypy src tests
pytest
```

Result: 71 tests passed.
