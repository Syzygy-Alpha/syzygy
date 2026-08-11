# SYZYGY Observatory

Observatory is the observability module of SYZYGY. Its long-term purpose is to
support logs, metrics, tracing, dashboards, alerts, and telemetry.

This first increment intentionally implements only local health visibility:

- HTTP health, version, and capabilities endpoints
- Observatory module descriptor
- optional registration with Foundation
- SQLite-backed health observation storage
- health summary endpoint

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

## Scope Boundary

Observatory v0.1 does not yet run Prometheus, Grafana, Loki, tracing, alerting,
or dashboards. Those remain future integrations after local contracts are
stable.
