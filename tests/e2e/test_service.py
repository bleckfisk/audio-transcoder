import json
from service.core import process_messages
from service.aws_boto3 import (
    listen_sqs_queue,
    create_sqs_resource,
    delete_message
)


from service.settings import (
    AWS_SQS_QUEUE_NAME
)


def test_service(setup_no_exceptions):
    response = listen_sqs_queue(
        create_sqs_resource(),
        AWS_SQS_QUEUE_NAME,
        process_messages,
        delete_message,
        True
    )

    callback = json.loads(response)
    assert callback["status"] == 'success'
    assert callback["errors"] is None


def test_service_fails_callback_still_runs(setup_error):
    response = listen_sqs_queue(
        create_sqs_resource(),
        AWS_SQS_QUEUE_NAME,
        process_messages,
        delete_message,
        True
    )

    callback = json.loads(response)
    assert callback["status"] == 'error'
    assert callback["errors"] is not None
