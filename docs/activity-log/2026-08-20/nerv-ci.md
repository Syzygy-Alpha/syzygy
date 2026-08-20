# NERV CI

## Context

NERV now has a dashboard, module actions, and a Forge project workbench. The
local virtual environment currently inherits an unusable Windows Store Python
base, preventing local execution of its quality commands.

Foundation and Forge already use GitHub Actions to run their quality gates in a
clean, reproducible environment. NERV needs the same verification path.

## Created

- Added a path-scoped NERV GitHub Actions workflow.
- Runs tests, Ruff, and mypy from `nerv/` on pull requests and pushes to `main`.
- Uses Python 3.12 with pip dependency caching.
- Limits the workflow token to read-only repository contents.

## Scope Boundary

This workflow validates NERV; it does not deploy it or make local module
controls available from GitHub. NERV operations remain local-first because they
control processes and projects on the user's computer.

## Validation

- Workflow structure follows the established Foundation and Forge CI pattern.
- `git diff --check` passed locally.
- Local pytest remains blocked before startup by the broken Windows Store Python
  base used by `.venv`; NERV CI provides the clean Python 3.12 verification
  path for this module.

## Follow-Up

- Corrected NERV Forge import ordering after the first CI run reported
  auto-fixable Ruff findings. The workflow remains check-only so a failed check
  always reflects the committed source rather than an ephemeral runner change.
- Removed the two unused imports and completed the import ordering specified by
  the Ruff output from that run.
