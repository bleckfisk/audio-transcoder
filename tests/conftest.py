from botocore.exceptions import ClientError
import pytest
from uuid import uuid4


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
        MessageBody=str(uuid4())
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
        MessageBody=str(uuid4())
    )

    yield queue_name
