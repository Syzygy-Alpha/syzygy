# Forge Practical Usage

This guide shows a local end-to-end Forge flow using `curl`.

Forge is still a local development service. Run it on a trusted loopback
interface and avoid exposing it to a network until authentication is added.

## Start Forge

```bash
cd forge
python -m pip install -e ".[dev]"
uvicorn syzygy_forge.main:app --reload --port 8010
```

Optional local settings:

```bash
set SYZYGY_FORGE_WORKSPACE_ROOT=C:\Users\Gustavo\Documents\Projetos
set SYZYGY_FORGE_DATABASE_URL=sqlite:///./data/forge.db
```

## Check The Service

```bash
curl http://127.0.0.1:8010/health
curl http://127.0.0.1:8010/version
curl http://127.0.0.1:8010/capabilities
```

## Create A Project

List templates:

```bash
curl http://127.0.0.1:8010/project-templates
```

Create a Python CLI project:

```bash
curl -X POST http://127.0.0.1:8010/projects/create ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"hello-tool\",\"template\":\"python-cli\",\"initialize_git\":true}"
```

Other local templates:

```bash
curl -X POST http://127.0.0.1:8010/projects/create ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"hello-package\",\"template\":\"python-package\",\"initialize_git\":true}"

curl -X POST http://127.0.0.1:8010/projects/create ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"hello-site\",\"template\":\"static-site\",\"initialize_git\":true}"
```

List registered projects:

```bash
curl http://127.0.0.1:8010/projects
curl http://127.0.0.1:8010/projects/hello-tool
```

## Run Declared Commands

Forge reads commands from `syzygy.project.toml`.

```bash
curl http://127.0.0.1:8010/projects/hello-tool/commands
curl http://127.0.0.1:8010/projects/hello-tool/commands/test/plan
```

Execute only after reviewing the plan:

```bash
curl -X POST http://127.0.0.1:8010/projects/hello-tool/commands/test/runs ^
  -H "Content-Type: application/json" ^
  -d "{\"confirm\":true,\"timeout_seconds\":30}"
```

Check command history:

```bash
curl http://127.0.0.1:8010/projects/hello-tool/command-runs
```

## Inspect Events

Confirmed command runs create local outbox events.

```bash
curl http://127.0.0.1:8010/events/outbox
curl http://127.0.0.1:8010/events/outbox/summary
curl "http://127.0.0.1:8010/events/outbox?status=pending"
```

Enable event publishing explicitly when needed:

```bash
set SYZYGY_FORGE_EVENT_PUBLISHER_ENABLED=true
set SYZYGY_FORGE_EVENT_PUBLISHER_TRANSPORT=memory
```

Then restart Forge and publish pending events:

```bash
curl -X POST http://127.0.0.1:8010/events/outbox/publish ^
  -H "Content-Type: application/json" ^
  -d "{\"confirm\":true,\"limit\":100}"
```

Requeue failed deliveries manually:

```bash
curl -X POST http://127.0.0.1:8010/events/outbox/requeue-failed ^
  -H "Content-Type: application/json" ^
  -d "{\"confirm\":true,\"limit\":100}"
```

## Register Forge With Foundation

Start Foundation first, then start Forge with registration enabled:

```bash
set SYZYGY_FORGE_REGISTER_WITH_FOUNDATION=true
set SYZYGY_FORGE_FOUNDATION_URL=http://127.0.0.1:8000
set SYZYGY_FORGE_FOUNDATION_USERNAME=admin
set SYZYGY_FORGE_FOUNDATION_PASSWORD=change-me
uvicorn syzygy_forge.main:app --reload --port 8010
```

Use development credentials only for local testing.
