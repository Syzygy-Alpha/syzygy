.PHONY: install dev test lint format typecheck docker-up docker-down

install:
	python -m pip install -e ".[dev]"

dev:
	python -m uvicorn syzygy_foundation.main:app --reload --host 127.0.0.1 --port 8000

test:
	python -m pytest

lint:
	python -m ruff check .

format:
	python -m ruff format .

typecheck:
	python -m mypy src tests

docker-up:
	docker compose up --build

docker-down:
	docker compose down
