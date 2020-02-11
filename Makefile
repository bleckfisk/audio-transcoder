
build:
	@docker-compose build

localstack:
	@docker-compose up -d localstack

transcoder:
	@docker-compose up -d transcoder

run:
	@make -s localstack
	@make -s transcoder

setup:
	@make -s build
	@make -s test
	@make -s transcoder
	@echo Transcoder and Localstack is now running.

coverage:
	@make -s localstack
	@docker-compose run --rm --entrypoint 'pytest --cov-report term-missing --cov=service' transcoder

test:
	@make -s localstack
	@docker-compose run --rm --entrypoint 'pytest -v -s' transcoder

