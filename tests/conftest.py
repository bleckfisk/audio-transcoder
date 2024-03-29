
from botocore.exceptions import ClientError
import pytest
import os
import json
from uuid import uuid4


"""
Conftest file for all unittests to make sure
the tests get data to work with in isolation
"""


VALID_DATA = {
    "id": str(uuid4()),
    "input": {
        "key": "file_example_WAV_10MG.wav",
        "bucket": "testbucket"
    },
    "outputs": [
        {
            "key": "file_example_WAV_10MG.flac",
            "format": "flac",
            "bucket": "testbucket"
        },
        {
            "key": "file_example_WAV_10MG.mp3",
            "format": "mp3",
            "bucket": "testbucket"
        },
    ]
}

INVALID_DATA = {
    "id": "123",
    "bad_input": {
        "key": "file_example_WAV_10MG.wav",
        "bucket": "testbucket"
    },
    "bad_outputs": [
        {
            "key": "file_example_WAV_10MG.flac",
            "format": "flac",
            "bucket": "testbucket"
        },
        {
            "key": "file_example_WAV_10MG.mp3",
            "format": "mp3",
            "bucket": "testbucket"
        },
    ]
}


@pytest.fixture
def s3_bucket():
    from service.aws_boto3 import create_s3_resource
    resource = create_s3_resource()

    bucket_name = str(uuid4())
    try:
        bucket = resource.create_bucket(Bucket=bucket_name)
    except ClientError:
        bucket = resource.Bucket(bucket_name)
        bucket.objects.all().delete()
    yield bucket
    bucket.objects.all().delete()
    bucket.delete()


@pytest.fixture
def sns_topic_arn():
    from service.aws_boto3 import create_sns_resource

    resource = create_sns_resource()
    topic_name = str(uuid4())
    response = resource.meta.client.create_topic(Name=topic_name)

    yield response["TopicArn"]
    resource.meta.client.delete_topic(
        TopicArn=response["TopicArn"]
    )


@pytest.fixture
def sqs_queue():
    from service.aws_boto3 import create_sqs_resource
    resource = create_sqs_resource()

    queue_name = str(uuid4())

    queue = resource.meta.client.create_queue(
        QueueName=queue_name
    )

    resource.meta.client.send_message(
        QueueUrl=queue.get("QueueUrl"),
        MessageBody=json.dumps(VALID_DATA)
    )

    yield queue


@pytest.fixture
def sqs_queue_bad_message_keys():
    from service.aws_boto3 import create_sqs_resource
    resource = create_sqs_resource()

    queue_name = str(uuid4())

    queue = resource.meta.client.create_queue(
        QueueName=queue_name
    )

    resource.meta.client.send_message(
        QueueUrl=queue.get("QueueUrl"),
        MessageBody=json.dumps(INVALID_DATA)
    )

    yield queue


@pytest.fixture
def sqs_queue_name():
    from service.aws_boto3 import create_sqs_resource
    resource = create_sqs_resource()

    queue_name = str(uuid4())

    queue = resource.meta.client.create_queue(
        QueueName=queue_name
    )

    resource.meta.client.send_message(
        QueueUrl=queue.get("QueueUrl"),
        MessageBody=json.dumps(VALID_DATA)
    )

    yield queue_name


@pytest.fixture
def sqs_queue_name_bad_message_keys():
    from service.aws_boto3 import create_sqs_resource
    resource = create_sqs_resource()

    queue_name = str(uuid4())

    queue = resource.meta.client.create_queue(
        QueueName=queue_name
    )

    resource.meta.client.send_message(
        QueueUrl=queue.get("QueueUrl"),
        MessageBody=json.dumps(INVALID_DATA)
    )

    yield queue_name


@pytest.fixture
def list_of_supported_files():
    testfiles_directory = f'{os.getcwd()}/tests/test_samples/supported'
    return os.listdir(testfiles_directory)


@pytest.fixture
def list_of_unsupported_files():
    testfiles_directory = f'{os.getcwd()}/tests/test_samples/unsupported'
    return os.listdir(testfiles_directory)
