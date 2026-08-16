# SYZYGY Observatory

Observatory is the observability module of SYZYGY. Its long-term purpose is to
support logs, metrics, tracing, dashboards, alerts, and telemetry.

This first increment intentionally implements only local health visibility:

- HTTP health, version, and capabilities endpoints
- Observatory module descriptor
- optional registration with Foundation
- SQLite-backed health observation storage
- health summary endpoint
- manual ingestion of Foundation module health through the `/modules` contract
- optional scheduled polling of Foundation module health

## Local Development

```bash
cd observatory
python -m pip install -e ".[dev]"
uvicorn syzygy_observatory.main:app --reload --port 8020
```

Useful endpoints:

```text
GET /
GET /health
GET /version
GET /capabilities
POST /health-observations
GET /health-observations
GET /health-observations/summary
POST /ingest/foundation/modules
GET /ingest/foundation/modules/polling
```

## Health Observations

`POST /health-observations` records a local health observation for a service or
module. It is intended for lightweight local visibility before adding a full
metrics/log stack.

Example payload:

```json
{
  "name": "forge",
  "status": "ok",
  "source": "manual",
  "details": {
    "url": "http://127.0.0.1:8010/health"
  }
}
```

`GET /health-observations/summary` returns total observations, counts by status,
and the latest observation per service.

## Foundation Module Ingestion

`POST /ingest/foundation/modules` reads Foundation's authenticated `/modules`
endpoint and records one local health observation per registered module.

This is intentionally manual in v0.1: Observatory does not poll Foundation on a
schedule yet, and the endpoint requires an explicit confirmation flag.

It uses the configured Foundation connection:

```text
SYZYGY_OBSERVATORY_FOUNDATION_URL
SYZYGY_OBSERVATORY_FOUNDATION_USERNAME
SYZYGY_OBSERVATORY_FOUNDATION_PASSWORD
SYZYGY_OBSERVATORY_FOUNDATION_MODULE_POLLING_ENABLED
SYZYGY_OBSERVATORY_FOUNDATION_MODULE_POLLING_INTERVAL_SECONDS
```

Example:

```bash
curl -X POST http://127.0.0.1:8020/ingest/foundation/modules \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

Then inspect the collected view:

```bash
curl http://127.0.0.1:8020/health-observations/summary
```

Polling is disabled by default. To let Observatory ingest Foundation module
health on a schedule, set:

```env
SYZYGY_OBSERVATORY_FOUNDATION_MODULE_POLLING_ENABLED=true
SYZYGY_OBSERVATORY_FOUNDATION_MODULE_POLLING_INTERVAL_SECONDS=60
```

Check polling state:

```bash
curl http://127.0.0.1:8020/ingest/foundation/modules/polling
```

## Scope Boundary

Observatory v0.1 does not yet run Prometheus, Grafana, Loki, tracing, alerting,
dashboards, or distributed telemetry. Those remain future integrations after
local contracts are stable.
