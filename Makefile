.PHONY: help install install-dev run start stop restart status logs test lint format clean docker-build docker-up docker-down

PYTHON ?= python3
VENV ?= venv
VENV_BIN ?= $(VENV)/bin
PIP ?= $(VENV_BIN)/pip
PYTEST ?= $(VENV_BIN)/pytest

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

$(VENV): ## Create virtual environment
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

install: $(VENV) ## Install production dependencies from pyproject.toml
	$(PIP) install .

install-dev: $(VENV) ## Install development and test dependencies from pyproject.toml
	$(PIP) install -e ".[dev]"

run: $(VENV) ## Run bot directly in foreground
	$(VENV_BIN)/python -u -m src

start: ## Start bot in background via scripts/manage.sh
	./scripts/manage.sh start

stop: ## Stop background bot process
	./scripts/manage.sh stop

restart: ## Restart background bot process
	./scripts/manage.sh restart

status: ## Check background bot status
	./scripts/manage.sh status

logs: ## View real-time bot logs
	./scripts/manage.sh logs

test: $(VENV) ## Run test suite using pytest
	$(PYTEST) -v tests/

lint: $(VENV) ## Check code style with ruff
	$(VENV_BIN)/ruff check src/ tests/

format: $(VENV) ## Format code with black and ruff
	$(VENV_BIN)/ruff check --fix src/ tests/
	$(VENV_BIN)/black src/ tests/

docker-build: ## Build Docker container
	docker compose build

docker-up: ## Start Docker container in background
	docker compose up -d

docker-down: ## Stop Docker container
	docker compose down

clean: ## Clean up cache, pyc, and temp files
	rm -rf __pycache__ src/__pycache__ tests/__pycache__
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage
	find . -type f -name "*.pyc" -delete
