.PHONY: help install dev-install test lint format clean run-backend run-frontend docker-up docker-down setup

help: ## Show this help message
	@echo "ARES - Autonomous Resilient Enterprise Suite"
	@echo "============================================="
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install --upgrade pip
	pip install -r requirements.txt
	python -m spacy download de_core_news_sm

dev-install: ## Install development dependencies
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e ".[dev]"
	python -m spacy download de_core_news_sm

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=src --cov-report=html --cov-report=term

lint: ## Run linters
	ruff check src tests
	mypy src

format: ## Format code
	black src tests
	ruff check --fix src tests

clean: ## Clean generated files
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/

run-backend: ## Start FastAPI backend
	uvicorn src.api.main:app --reload --port 8000

run-frontend: ## Start Streamlit frontend
	streamlit run src/ui/app.py

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

setup: ## Initial setup (create directories, copy .env)
	mkdir -p data chroma_db uploads
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "⚠️  Please edit .env with your configuration"; \
	fi

all: clean install setup ## Clean, install, and setup
