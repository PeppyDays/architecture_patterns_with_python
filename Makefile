export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

all: down build up test

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down --remove-orphans

test:
	pytest --tb=short

unit-test:
	pytest --tb=short tests/unit

integration-test:
	pytest --tb=short tests/integration

e2e-test:
	pytest --tb=short tests/e2e

logs:
	docker compose logs api | tail -100

black:
	black $$(find * -name '*.py')
