import pytest
import boto3
from uuid import uuid4
from botocore.exceptions import ClientError
from service.aws_boto3 import (
    create_sns_resource,
    create_s3_resource,
    create_sqs_resource,
    listen_sqs_queue,
    publish_sns
)

from service.settings import (
    AWS_SQS_ENDPOINT_URL
)

from unittest import mock


def test_create_sqs_resource():
    client_1 = boto3.resource('sqs', endpoint_url=AWS_SQS_ENDPOINT_URL)
    client_2 = create_sqs_resource()
    assert client_1 == client_2


def test_create_s3_resource():
    client_1 = boto3.resource('s3', endpoint_url=AWS_SQS_ENDPOINT_URL)
    client_2 = create_s3_resource()
    assert client_1 == client_2


def test_create_sns_resource():
    client_1 = boto3.resource('sns', endpoint_url=AWS_SQS_ENDPOINT_URL)
    client_2 = create_sns_resource()
    assert client_1 == client_2


def test_publish_sns(sns_topic_arn):
    message = str(uuid4())
    publish_sns(create_sns_resource(), sns_topic_arn, message)


def test_publish_sns_topic_not_found(sns_topic_arn):
    message = str(uuid4())
    non_existant_topic = str(uuid4())

    with pytest.raises(ClientError):
        publish_sns(create_sns_resource(), non_existant_topic, message)


def test_delete_message(sqs_queue):
    """
    Test recieves a message, deletes in and then recieves messages again.
    Asserts that the second response doesn't contain any message.
    """
    resource = create_sqs_resource()

    messages_1 = resource.meta.client.receive_message(
        QueueUrl=sqs_queue.get("QueueUrl"),
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0
    )

    receipthandle_1 = messages_1["Messages"][0]["ReceiptHandle"]

    resource.meta.client.delete_message(
        QueueUrl=sqs_queue.get("QueueUrl"),
        ReceiptHandle=receipthandle_1
    )

    messages_2 = resource.meta.client.receive_message(
        QueueUrl=sqs_queue.get("QueueUrl"),
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0
    )

    assert "Messages" not in messages_2


def test_listen_sqs_queue(sqs_queue_name):
    """
    Sends mocked functions to listen_sqs_queue()
    to assert that listen_sqs_queue() is really calling functions
    without having to run them
    """

    process_message_mock = mock.Mock()

    listen_sqs_queue(
        create_sqs_resource(),
        sqs_queue_name,
        process_message_mock,
        run_once=True
    )

    process_message_mock.assert_called_once()


@mock.patch('service.core.callback')
@mock.patch('service.loggers.Service_Logger')
def test_listen_sqs_queue_bad_message_keys(
    logger_mock,
    callback_mock,
    sqs_queue_name_bad_message_keys
        ):

    """
    This test proves that when exception is raised due to bad keys
    we call the callback function and deletes the message even if it
    isn't fully processed.
    """
    sqs_queue_name = sqs_queue_name_bad_message_keys
    process_message_mock = mock.Mock(side_effect=Exception)

    listen_sqs_queue(
        create_sqs_resource(),
        sqs_queue_name,
        process_message_mock,
        run_once=True
    )

    assert process_message_mock.call_count == 1
    assert callback_mock.call_count == 1
