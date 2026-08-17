.PHONY: install dev test lint format typecheck

install:
	python -m pip install -e ".[dev]"

dev:
	uvicorn syzygy_mycelium.main:app --reload --host 127.0.0.1 --port 8030

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy src tests
