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
