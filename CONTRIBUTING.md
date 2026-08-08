# Contributing To SYZYGY

SYZYGY grows through small, documented increments.

## Before Changing Code

1. Read `AGENTS.md`.
2. Inspect the repository.
3. Identify the affected module.
4. Identify existing contracts, tests, and docs.
5. Choose the smallest useful change.

## Commits

Use Conventional Commits:

```text
feat:
fix:
docs:
refactor:
test:
perf:
ci:
style:
build:
chore:
```

Prefer small commits that describe one coherent increment.

## Activity Logs

Meaningful increments should add one file under:

```text
docs/activity-log/
```

The log should explain:

- what changed
- why it changed
- how it was validated
- what remains out of scope

## Quality

For Foundation changes, run from `foundation/`:

```bash
python -m pytest
python -m ruff check .
python -m mypy src tests
```

Docker should be checked when Docker is available and the change affects the
runtime.

