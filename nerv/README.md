# SYZYGY NERV

NERV is the operational center of SYZYGY. Its long-term purpose is to become
the dashboard for modules, internal apps, services, devices, and routine
operations.

This first increment intentionally implements a lightweight local command
center:

- HTTP health, version, and capabilities endpoints
- NERV module descriptor
- optional registration with Foundation
- zero-build dashboard served by FastAPI
- local module catalog for known SYZYGY surfaces
- local start/stop actions for known module development servers
- quick actions for common module endpoint reads
- live reachability checks and optional Foundation registry visibility

## Local Development

```bash
cd nerv
python -m pip install -e ".[dev]"
python -m uvicorn syzygy_nerv.main:app --reload --port 8040
```

Useful endpoints:

```text
GET /
GET /health
GET /version
GET /capabilities
GET /api/dashboard
POST /api/surfaces/{name}/start
POST /api/surfaces/{name}/stop
POST /api/surfaces/{name}/actions/{action_name}/run
```

## Dashboard

The root page serves a lightweight local dashboard with:

- cards for known SYZYGY modules
- launch and stop buttons for supported local module servers
- quick action buttons for frequently used module reads
- direct links to root, health, and capabilities endpoints
- quick operational state from live HTTP probes
- optional Foundation registry information when enabled

Known modules are currently:

- Foundation
- Forge
- Observatory
- Mycelium
- NERV

Known quick actions currently include examples such as:

- Foundation health and version
- Forge current project, projects, and outbox summary
- Observatory health summary, trends, and polling status
- Mycelium local node and known peers
- NERV dashboard state and capabilities

## Local Actions

NERV uses explicit local commands for known modules. It does not shell out
through `make` or require a frontend build tool.

By default it launches module servers with:

```text
python -m uvicorn <package>.main:app --host 127.0.0.1 --port <port>
```

You can override the Python executable with:

```text
SYZYGY_NERV_PYTHON_EXECUTABLE
```

Runtime logs are written under:

```text
SYZYGY_NERV_RUNTIME_LOGS_DIR
```

## Quick Actions

NERV keeps quick actions explicit and catalog-driven. It does not expose a
generic arbitrary request UI; instead, it offers curated reads for the known
module contracts already documented in the repository.

Quick actions return their response inline in the dashboard's operations
console, so common operational queries no longer require manually opening each
endpoint one by one.

## Foundation Registry

NERV can optionally register itself with Foundation and optionally read
Foundation's authenticated `/modules` registry contract:

```env
SYZYGY_NERV_REGISTER_WITH_FOUNDATION=true
SYZYGY_NERV_FOUNDATION_REGISTRY_ENABLED=true
SYZYGY_NERV_FOUNDATION_URL=http://127.0.0.1:8000
SYZYGY_NERV_FOUNDATION_USERNAME=admin
SYZYGY_NERV_FOUNDATION_PASSWORD=change-me
```

## Scope Boundary

NERV v0.1 does not yet include React, Material UI, device orchestration,
container management, authentication hardening, persistent action history, or
internal app launchers beyond the known module catalog. This increment is a
light local-first dashboard and launcher spine that can be upgraded later.
