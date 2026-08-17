# SYZYGY Foundation

Foundation is the first functional module of SYZYGY. It provides the shared core for
configuration, health, versioning, basic authentication, persistence, events,
scheduling, and module lifecycle contracts.

This MVP intentionally avoids implementing future modules such as Mycelium,
Coppermind, MAGI, NERV, Tungsten, or Bastion.

## Local Development

```bash
cd foundation
cp .env.example .env
python -m pip install -e ".[dev]"
python -m uvicorn syzygy_foundation.main:app --reload
```

Useful endpoints:

```text
GET  /
GET  /health
GET  /version
POST /auth/token
GET  /auth/me
POST /modules/register
GET  /modules
GET  /modules/{name}
PATCH /modules/{name}/status
PATCH /modules/{name}/health
```

Module registry endpoints require a bearer token from `/auth/token`.

## Docker

```bash
cd foundation
docker compose up --build
```

The development compose stack starts Foundation and NATS. Copy `.env.example`
to `.env` when you want to override the default development values.

## Quality

```bash
python -m pytest
python -m ruff check .
python -m mypy src tests
```

## Security Notes

The values in `.env.example` are development defaults only. Do not use the sample
JWT secret or admin password in shared or production environments.
