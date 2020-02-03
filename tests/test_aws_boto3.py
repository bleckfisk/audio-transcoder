import pytest
import boto3
from uuid import uuid4
from botocore.exceptions import ClientError
from service.aws_boto3 import (
    create_sns_resource,
    create_s3_resource,
    create_sqs_resource,
    listen_sqs_queue,
    publish_sns,
    delete_message
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
    resource = create_sqs_resource()

    messages_1 = resource.meta.client.receive_message(
        QueueUrl=sqs_queue.get("QueueUrl"),
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0
    )

    receipthandle_1 = messages_1["Messages"][0]["ReceiptHandle"]

    delete_message(resource, sqs_queue, receipthandle_1)

    messages_2 = resource.meta.client.receive_message(
        QueueUrl=sqs_queue.get("QueueUrl"),
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0
    )

    assert "Messages" not in messages_2


def test_listen_sqs_queue(sqs_queue_name):

    process_messages_mock = mock.Mock(return_value=['', ''])
    delete_message_mock = mock.Mock()

    listen_sqs_queue(
        create_sqs_resource(),
        sqs_queue_name,
        process_messages_mock,
        delete_message_mock,
        run_once=True
    )

    delete_message_mock.assert_called_once()
    process_messages_mock.assert_called_once()
