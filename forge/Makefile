.PHONY: install dev test lint format typecheck

install:
	python -m pip install -e ".[dev]"

dev:
	uvicorn syzygy_forge.main:app --reload --host 127.0.0.1 --port 8010

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy src tests

