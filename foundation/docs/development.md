# Development Guide

## Requirements

- Python 3.11+
- Docker and Docker Compose for the full development stack

## Local Setup

```bash
cd foundation
cp .env.example .env
python -m pip install -e ".[dev]"
```

## Run Locally

```bash
uvicorn syzygy_foundation.main:app --reload --host 127.0.0.1 --port 8000
```

## Run With Docker

```bash
docker compose up --build
```

Ports:

- Foundation HTTP API: `8000`
- NATS client port: `4222`
- NATS monitoring: `8222`

## Test And Quality Commands

```bash
pytest
ruff check .
ruff format .
mypy src tests
```

## CI

GitHub Actions runs the Foundation test, lint, and type-check commands on pushes
to `main` and on pull requests when Foundation files change.

## Environment

Copy `.env.example` to `.env` for development. The sample JWT secret and admin
password are local defaults only and must be replaced for shared environments.

## Persistence Migrations

Foundation uses a small SQLite migration runner in code. Migrations are applied
when the database initializes and tracked in `foundation_schema_migrations`.

This keeps the MVP local-first and dependency-light. If the schema becomes more
complex, the project can revisit a dedicated migration tool through an ADR.

## Module Registry

Foundation persists module descriptors in SQLite. The registry is the current
contract for future modules to declare their version, status, health,
capabilities, dependencies, and latest known activity.

Authenticated module endpoints:

```text
POST  /modules/register
GET   /modules
GET   /modules/{name}
PATCH /modules/{name}/status
PATCH /modules/{name}/health
```
