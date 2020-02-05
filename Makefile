coverage:
	@docker-compose run --rm --entrypoint 'pytest --cov=service' transcoder

test:
	@docker-compose run --rm --entrypoint 'pytest -v -s' transcoder

build:
	@docker-compose build

setup:
	@docker-compose build
	@docker-compose up -d localstack
	@docker-compose run --rm --entrypoint 'pytest -v -s' transcoder
	@docker-compose up -d transcoder
	@echo Transcoder and Localstack is now running.