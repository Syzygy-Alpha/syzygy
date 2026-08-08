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
