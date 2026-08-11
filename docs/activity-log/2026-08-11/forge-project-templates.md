# 2026-08-11 - Forge Project Templates

## Context

Forge could create projects only from the `python-cli` template. That made the
project creation flow useful but too narrow for real local experimentation.

## Created

- `python-package` template.
- `static-site` template.
- Tests for creating projects from the new templates.
- API template listing expectation updated.
- README and practical usage guide updated with the available templates.

## What It Does Now

Forge can create three local project shapes:

- `python-cli`
- `python-package`
- `static-site`

Each template includes a `syzygy.project.toml` manifest with commands compatible
with Forge's current command safety policy.

## Scope Boundary

No external package manager, JavaScript build tool, Docker template, or cloud
deployment path was added. Templates remain local-first and dependency-light.

## Validation

Validated with:

```text
ruff check .
mypy src tests
pytest
```

Result: 62 tests passed.
