# Python Module Entrypoints

## Context

Running `uvicorn` directly failed on Windows because the executable was not
available on `PATH`, even though the project can still be run through Python's
module entrypoint.

## Updated

- Replaced direct `uvicorn` commands in module READMEs with
  `python -m uvicorn`.
- Updated module Makefiles to use `python -m pytest`, `python -m ruff`,
  `python -m mypy`, and `python -m uvicorn`.
- Applied the same convention to Foundation, Forge, Observatory, and Mycelium.

## Why

`python -m ...` is more reliable on Windows because it uses the selected Python
environment directly and does not require console scripts to be discoverable on
`PATH`.

## Validation

Documentation and command-wrapper change only.

- `git diff --check` passed.
- `python -m uvicorn --help` worked from the Mycelium directory using the
  available project Python environment.
