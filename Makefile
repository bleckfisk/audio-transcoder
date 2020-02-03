coverage:
	@docker-compose run --rm --entrypoint 'pytest --cov=service' transcoder

test:
	@docker-compose run --rm --entrypoint 'pytest -v' transcoder
