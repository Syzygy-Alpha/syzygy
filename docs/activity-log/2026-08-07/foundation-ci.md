# 2026-08-07 - Foundation CI

## Context

Foundation v0.1 has local tests, linting, and type checking. The next small
increment is to make those quality gates reproducible in GitHub.

## Created

- GitHub Actions workflow for Foundation.

## What It Does Now

The workflow runs on pushes to `main` and pull requests when Foundation or the
workflow file changes.

It executes:

```text
python -m pytest
python -m ruff check .
python -m mypy src tests
```

## Scope Boundary

This does not add deployment, containers, security scanning, release automation,
or Forge automation. Those remain future increments.

## Validation

Validated locally with the same Foundation quality commands before commit.

