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
- Forge project workbench for declared project commands
- live reachability checks and optional Foundation registry visibility

## Local Development

```bash
cd nerv
python -m pip install -e ".[dev]"
python -m uvicorn syzygy_nerv.main:app --reload --port 8040
```

## Continuous Integration

GitHub Actions runs NERV tests, lint, and type checks on pull requests and on
pushes to `main` that affect `nerv/`. The workflow provides reproducible remote
validation, but it does not deploy the dashboard: NERV controls local processes
and remains a local-first service.

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
GET /api/forge/projects
GET /api/forge/commands/plan?project={name}&command={name}
POST /api/forge/commands/run?project={name}&command={name}&confirm=true
```

## Dashboard

The root page serves a lightweight local dashboard with:

- cards for known SYZYGY modules
- launch and stop buttons for supported local module servers
- quick action buttons for frequently used module reads
- direct links to root, health, and capabilities endpoints
- quick operational state from live HTTP probes
- optional Foundation registry information when enabled
- registered Forge projects and their declared commands

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

## Forge Project Workbench

When Forge is running, NERV reads its registered project and command contracts
to render a local project workbench. Select `PLAN` to inspect the exact plan
from Forge. Select `RUN` only after reviewing it; NERV asks for browser
confirmation, requires `confirm=true` on its API, and asks Forge for a fresh
allowed plan before it delegates execution.

NERV does not gain direct filesystem or shell access from this feature. Forge
remains responsible for allow-list policy, execution timeouts, and command
history.

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
internal app lifecycle management. This increment is a light local-first
dashboard and launcher spine that can be upgraded later.
