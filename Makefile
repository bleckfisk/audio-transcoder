coverage:
	pytest --cov=service -v

test:
	pytest

localstack:
	docker-compose up localstack

transcoder:
	docker-compose up transcoder

run:
	docker-compose up

detach:
	docker-compose up -d
	