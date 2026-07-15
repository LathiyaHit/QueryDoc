.PHONY: dev frontend test build migrate lint clean ingest

dev:
	docker-compose up -d redis postgres qdrant jaeger
	cd services/api && uvicorn main:app --reload --port 8000

frontend:
	python frontend/app.py

ingest:
	python scripts/ingest_default_pdf.py

test:
	pytest tests/ -v --cov=services --cov-report=term-missing

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

migrate:
	cd services/api && alembic upgrade head

migrate-new:
	cd services/api && alembic revision --autogenerate -m "$(msg)"

lint:
	ruff check .
	black --check .

format:
	black .
	ruff check --fix .

install:
	pip install -e .
	pip install -r requirements-dev.txt

build:
	docker-compose build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name ".pytest_cache" -exec rm -rf {} +
