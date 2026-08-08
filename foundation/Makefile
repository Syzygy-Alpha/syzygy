.PHONY: install dev test lint format typecheck docker-up docker-down

install:
	python -m pip install -e ".[dev]"

dev:
	uvicorn syzygy_foundation.main:app --reload --host 127.0.0.1 --port 8000

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy src tests

docker-up:
	docker compose up --build

docker-down:
	docker compose down

