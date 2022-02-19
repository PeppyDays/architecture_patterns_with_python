export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

build:
	#docker compose -f containers/docker-compose.yaml build
	docker compose build

up:
	#docker compose -p allocation -f containers/docker-compose.yaml up -d
	docker compose -p allocation up -d

down:
	#docker compose -f containers/docker-compose.yaml down
	docker compose -p allocation down

logs:
	#docker compose -f containers/docker-compose.yaml logs api | tail -100
	docker compose logs api | tail -100

test:
	pytest --tb=short

black:
	black $$(find * -name '*.py')
