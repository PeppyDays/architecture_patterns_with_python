build:
	docker compose -f containers/docker-compose.yaml build

up:
	docker compose -p allocation -f containers/docker-compose.yaml up -d

down:
	docker compose -f containers/docker-compose.yaml down

logs:
	docker compose -f containers/docker-compose.yaml logs api | tail -100

test:
	pytest --tb=short

black:
	black $$(find * -name '*.py')
