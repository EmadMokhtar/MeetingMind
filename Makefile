.PHONY: help install test tests lint format run clean

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies (uv sync)"
	@echo "  make test     - Run tests"
	@echo "  make tests    - Alias for test"
	@echo "  make lint     - Run linter"
	@echo "  make format   - Format code"
	@echo "  make run      - Run the watcher"
	@echo "  make clean    - Clean build artifacts"

install:
	uv sync

test:
	uv run pytest tests/ -v

tests: test

lint:
	uv run ruff check .

format:
	uv run ruff format .
	uv run ruff check --fix .

run:
	uv run meetingmind watch

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
