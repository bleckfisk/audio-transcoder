coverage:
	@docker-compose run --rm --entrypoint 'pytest --cov=service' transcoder

test:
	@docker-compose run --rm --entrypoint 'pytest -v' transcoder

build:
	docker-compose build

setup:
	docker-compose build
	docker-compose up -d localstack
	pytest -v
	docker-compose up -d transcoder
	echo Transcoder is now running.