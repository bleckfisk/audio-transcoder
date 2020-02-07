import pytest
from uuid import uuid4
import os
import json
from botocore.exceptions import ClientError
from service.aws_boto3 import (
    create_s3_resource,
    create_sns_resource,
    create_sqs_resource
    )

from service.settings import (
    AWS_SNS_TOPIC_ARN,
    AWS_SQS_QUEUE_NAME,
)


@pytest.fixture
def setup_no_exceptions():
    """
    Will create bucket, upload file, create queue, send message and create
    topic for the test_service() test that will initiate a process
    as the software is intended to be used.
    """
    s3 = create_s3_resource()
    bucket_name = str(uuid4())

    try:
        bucket = s3.create_bucket(Bucket=bucket_name)
    except ClientError:
        bucket = s3.Bucket(bucket_name)

    data = {
        "input": {
            "key": "unique_id.wav",
            "bucket": bucket_name
        },
        "outputs": [
            {
                "key": "unique_id.flac",
                "format": "flac",
                "bucket": bucket_name
            },
            {
                "key": "unique_id.mp3",
                "format": "mp3",
                "bucket": bucket_name
            }
        ]
    }

    file = f"{os.getcwd()}/tests/test_samples/supported/sound.wav"
    s3.meta.client.upload_file(file, bucket_name, data["input"]["key"])

    sqs = create_sqs_resource()
    queue = sqs.meta.client.create_queue(QueueName=AWS_SQS_QUEUE_NAME)
    sqs.meta.client.send_message(
        QueueUrl=queue.get("QueueUrl"),
        MessageBody=json.dumps(data)
    )

    sns = create_sns_resource()
    topic_arn = AWS_SNS_TOPIC_ARN
    topic_name = get_topic_name_by_arn(topic_arn)
    response = sns.meta.client.create_topic(
        Name=topic_name
    )

    assert response["TopicArn"] == topic_arn
    yield bucket
    bucket.objects.all().delete()
    bucket.delete()


@pytest.fixture
def setup_error():
    """
    Will create bucket, upload file, create queue, send message and create
    topic for the test_service() test that will initiate a process
    as the software is intended to be used.
    """
    s3 = create_s3_resource()
    bucket_name = str(uuid4())

    try:
        bucket = s3.create_bucket(Bucket=bucket_name)
    except ClientError:
        bucket = s3.Bucket(bucket_name)

    data = {
        "input": {
            "key": str(uuid4()),
            "bucket": bucket_name
        },
        "outputs": [
            {
                "key": str(uuid4()),
                "format": "flac",
                "bucket": bucket_name
            },
            {
                "key": str(uuid4()),
                "format": "mp3",
                "bucket": bucket_name
            }
        ]
    }

    file = f"{os.getcwd()}/tests/test_samples/unsupported/Test.pdf"
    s3.meta.client.upload_file(file, bucket_name, data["input"]["key"])

    sqs = create_sqs_resource()
    queue = sqs.meta.client.create_queue(QueueName=AWS_SQS_QUEUE_NAME)
    sqs.meta.client.send_message(
        QueueUrl=queue.get("QueueUrl"),
        MessageBody=json.dumps(data)
    )

    sns = create_sns_resource()
    topic_arn = AWS_SNS_TOPIC_ARN
    topic_name = get_topic_name_by_arn(topic_arn)
    response = sns.meta.client.create_topic(
        Name=topic_name
    )

    assert response["TopicArn"] == topic_arn
    yield bucket
    bucket.objects.all().delete()
    bucket.delete()


def get_topic_name_by_arn(topic_arn):
    """
    function for handling the somewhat tricky
    built topic-arns used for topic targeting
    """
    i = 0
    topic_name = ''
    for character in topic_arn:
        if i == 5:
            topic_name += character
        if character == ":":
            i += 1

    return topic_name
