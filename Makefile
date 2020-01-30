coverage:
	docker-compose up -d localstack
	pytest --cov=service -v

test:
	docker-compose up -d localstack
	pytest

down: 
	docker-compose down

localstack:
	docker-compose up localstack

run:
	docker-compose up

detach:
	docker-compose up -d

local-run: 
	python -m service

s3-bucket:
	python tests/actions/s3_create_bucket.py

s3-file:
	python tests/actions/s3_upload_file.py

sns:
	python tests/actions/sns_create_topic.py

sqs:
	python tests/actions/sqs_create_queue.py
	python tests/actions/sqs_send_message.py
