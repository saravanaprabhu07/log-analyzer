.PHONY: help install dev test lint format clean docker-build docker-up docker-down db-init

help:
	@echo "Intelligent Log Analyzer - Development Commands"
	@echo "================================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install         - Install dependencies"
	@echo "  make dev             - Setup development environment"
	@echo ""
	@echo "Running:"
	@echo "  make run             - Run development server"
	@echo "  make run-prod        - Run production server"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test            - Run tests"
	@echo "  make lint            - Run linting (flake8, pylint)"
	@echo "  make format          - Format code with black"
	@echo "  make type-check      - Run type checking with mypy"
	@echo "  make quality         - Run all quality checks"
	@echo ""
	@echo "Database:"
	@echo "  make db-init         - Initialize database"
	@echo "  make db-clean        - Clean database"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build    - Build Docker image"
	@echo "  make docker-up       - Start containers with Docker Compose"
	@echo "  make docker-down     - Stop Docker containers"
	@echo "  make docker-logs     - View Docker logs"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean           - Remove build artifacts and cache files"
	@echo "  make requirements    - Update requirements.txt"

# Installation
install:
	pip install --upgrade pip
	pip install -r requirements.txt

dev: install
	cp .env.example .env
	python setup.py
	@echo "✅ Development environment ready!"

# Running
run:
	uvicorn main:app --reload --port 8000

run-prod:
	uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Testing
test:
	pytest -v --cov=. tests/

test-fast:
	pytest -v --tb=short

coverage:
	pytest --cov=. --cov-report=html tests/
	@echo "📊 Coverage report generated in htmlcov/index.html"

# Linting and Formatting
lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	pylint main.py config.py models/ routes/ utils/ core/

format:
	black . --line-length 100

isort:
	isort . --profile black

type-check:
	mypy main.py config.py models/ routes/ utils/ core/ --ignore-missing-imports

quality: format isort lint type-check
	@echo "✅ All quality checks passed!"

# Database
db-init:
	python -c "from models.database import init_db; init_db()"
	@echo "✅ Database initialized!"

db-clean:
	rm -f intelligent_logs.db
	@echo "✅ Database cleaned!"

db-reset: db-clean db-init

# Docker
docker-build:
	docker build -t intelligent-log-analyzer:latest .
	@echo "✅ Docker image built!"

docker-up:
	docker-compose up -d
	@echo "✅ Containers started!"
	@echo "📖 Access: http://localhost:8000/docs"

docker-down:
	docker-compose down
	@echo "✅ Containers stopped!"

docker-logs:
	docker-compose logs -f log-analyzer

docker-clean:
	docker-compose down -v
	docker rmi intelligent-log-analyzer:latest
	@echo "✅ Docker cleaned!"

# Utilities
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	@echo "✅ Cleaned up!"

requirements:
	pip list --outdated
	pip freeze > requirements.txt
	@echo "✅ requirements.txt updated!"

# Development utilities
shell:
	python -i -c "from models.database import SessionLocal, get_db; from sqlalchemy import text; db = SessionLocal(); print('Database shell ready. Use: db.execute(text(\"SELECT ...\"))')"

# CI/CD
ci: quality test
	@echo "✅ All CI checks passed!"

# Documentation
docs:
	@echo "📖 API Documentation: http://localhost:8000/docs"
	@echo "📖 ReDoc: http://localhost:8000/redoc"
	@echo "📖 OpenAPI Schema: http://localhost:8000/openapi.json"
