.DEFAULT_GOAL := help

.PHONY: help

help:
	@echo "CloudOps AI — Available Commands"
	@echo ""
	@echo "  make check     Verify required development tools"
	@echo "  make setup     Initialize project configuration safely"
	@echo "  make status    Show Docker service status"
	@echo "  make smoke     Run deployment health checks"
	@echo "  make up        Build and start the monitoring stack"
	@echo "  make down      Stop the monitoring stack"
	@echo "  make install   Install the Python package"
	@echo "  make run       Build and start Docker services"
	@echo "  make view      Show service URLs"
	@echo "  make test      Run automated tests"
	@echo "  make logs      Follow Docker service logs"
	@echo "  make stop      Stop Docker services"
	@echo "  make clean     Stop services and remove orphan containers"
	@echo ""
	@echo "More deployment commands will be added progressively."

.PHONY: install run view clean test stop logs

install:
	python -m pip install -e .

run:
	docker compose up -d --build

view:
	@echo "Flask Health: http://localhost:8000/health"
	@echo "Incident API: http://localhost:8000/api/incidents"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3000"

test:
	python -m pytest tests/ -q

logs:
	docker compose logs -f

stop:
	docker compose down

clean:
	docker compose down --remove-orphans

.PHONY: check

check:
	@echo "Checking CloudOps AI prerequisites..."
	@command -v python3 >/dev/null 2>&1 || { echo "FAIL: Python 3 not found"; exit 1; }
	@echo "PASS: Python 3"
	@command -v git >/dev/null 2>&1 || { echo "FAIL: Git not found"; exit 1; }
	@echo "PASS: Git"
	@command -v docker >/dev/null 2>&1 || { echo "FAIL: Docker not found"; exit 1; }
	@echo "PASS: Docker"
	@docker compose version >/dev/null 2>&1 || { echo "FAIL: Docker Compose not available"; exit 1; }
	@echo "PASS: Docker Compose"
	@docker info >/dev/null 2>&1 || { echo "FAIL: Docker daemon unavailable"; exit 1; }
	@echo "PASS: Docker daemon"
	@echo "All prerequisites passed."

.PHONY: setup

setup: check
	@python3 scripts/setup.py

.PHONY: status

status:
	@docker compose ps

.PHONY: up down

up: run

down: stop

.PHONY: smoke

smoke:
	@python3 scripts/smoke.py
