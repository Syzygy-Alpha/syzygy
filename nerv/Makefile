.PHONY: install dev test lint format typecheck

install:
	python -m pip install -e ".[dev]"

dev:
	python -m uvicorn syzygy_nerv.main:app --reload --host 127.0.0.1 --port 8040

test:
	python -m pytest

lint:
	python -m ruff check .

format:
	python -m ruff format .

typecheck:
	python -m mypy src tests
