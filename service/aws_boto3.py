from botocore.exceptions import ClientError
import boto3
from .settings import (
    AWS_SQS_ENDPOINT_URL,
    AWS_S3_ENDPOINT_URL,
    AWS_SNS_ENDPOINT_URL
)


def create_sqs_resource():
    return boto3.resource('sqs', endpoint_url=AWS_SQS_ENDPOINT_URL)


def create_s3_resource():
    return boto3.resource('s3', endpoint_url=AWS_S3_ENDPOINT_URL)


def create_sns_resource():
    return boto3.resource('sns', endpoint_url=AWS_SNS_ENDPOINT_URL)


def listen_sqs_queue(resource, queue_name, process_messages):
    queue = resource.meta.client.create_queue(QueueName=queue_name)

    while True:
        print("neverending story, nanana nanana nanana")
        messages = resource.meta.client.receive_message(
            QueueUrl=queue.get("QueueUrl"),
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )
        if 'Messages' in messages:
            print("There are messages")
            process_messages(messages)


def publish_sns(resource, topicarn, message):
    # publish notification to topic
    try:
        resource.meta.client.publish(
            TopicArn=topicarn,
            Message=message
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "NotFound":
            raise
