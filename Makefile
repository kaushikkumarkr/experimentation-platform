.PHONY: up down setup install test dagster-dev

include .env.example
export $(shell sed 's/=.*//' .env.example)

install:
	pip install -e .

setup:
	cp .env.example .env

up:
	docker-compose up -d

down:
	docker-compose down

dagster-dev:
	dagster dev -f orchestration/dagster_app/defs.py -p 3000

ingest:
	dagster asset materialize -f orchestration/dagster_app/defs.py -m raw_criteo_uplift


test:
	pytest tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
