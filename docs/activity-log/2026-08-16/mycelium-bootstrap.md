# Mycelium Bootstrap

## Context

After adding a vertical evolution cadence, the project needed to avoid staying
inside Observatory for another small refinement. Mycelium is the next official
module in the architecture order after Foundation and Forge, and it can receive
a minimal local-first bootstrap without implementing real distributed sync yet.

## Created

- Added the `mycelium/` module.
- Added FastAPI health, version, capabilities, and local node endpoints.
- Added a local Hypha node descriptor.
- Added optional Foundation module registration.
- Added settings, `.env.example`, Makefile, README, and tests.
- Updated project README, architecture, modules, roadmap, and activity log.

## What It Does Now

Mycelium can run locally as a service on port `8030`, describe itself as a
SYZYGY module, expose the local Hypha node identity, and optionally register
with Foundation.

Useful endpoints:

```text
GET /
GET /health
GET /version
GET /capabilities
GET /node
```

## Scope Boundary

This does not add Syncthing, WireGuard, Tailscale, gRPC, discovery, replication,
backup, or file synchronization. Those remain future work after the local node
contract is stable.

## Validation

- `python -m ruff check .` passed.
- `python -m mypy src tests` passed.
- `python -m pytest --basetemp .pytest-tmp -o cache_dir=.tmp/pytest_cache`
  passed with 5 tests.
- Pytest emitted a Windows cache warning, but the suite completed successfully.
