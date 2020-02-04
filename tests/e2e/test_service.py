import json
from unittest import mock
from service.core import process_messages
from service.aws_boto3 import (
    listen_sqs_queue,
    create_sqs_resource,
    delete_message,
    publish_sns
)


from service.settings import (
    AWS_SQS_QUEUE_NAME
)


@mock.patch("service.aws_boto3.publish_sns")
def test_service(mock_publish_sns, setup_no_exceptions):
    listen_sqs_queue(
        create_sqs_resource(),
        AWS_SQS_QUEUE_NAME,
        process_messages,
        delete_message,
        True
    )

    assert mock_publish_sns.call_count == 1


@mock.patch("service.aws_boto3.publish_sns")
def test_service_fails_callback_still_runs(mock_publish_sns, setup_error):
    listen_sqs_queue(
        create_sqs_resource(),
        AWS_SQS_QUEUE_NAME,
        process_messages,
        delete_message,
        True
    )

    assert mock_publish_sns.call_count == 1
