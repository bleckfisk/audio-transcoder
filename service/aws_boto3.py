from botocore.exceptions import ClientError
import boto3
from .settings import (
    AWS_SQS_ENDPOINT_URL,
    AWS_S3_ENDPOINT_URL,
    AWS_SNS_ENDPOINT_URL
)


"""
Following functions are data passing functions for AWS
that are a requirement for the core part of the service.
"""


def create_sqs_resource():
    # returns a resource (that contains a client) used to connect to SQS
    return boto3.resource('sqs', endpoint_url=AWS_SQS_ENDPOINT_URL)


def create_s3_resource():
    # returns a resource (that contains a client) used to connect to S3
    return boto3.resource('s3', endpoint_url=AWS_S3_ENDPOINT_URL)


def create_sns_resource():
    # returns a resource (that contains a client) used to connect to SNS
    return boto3.resource('sns', endpoint_url=AWS_SNS_ENDPOINT_URL)


def listen_sqs_queue(
    resource, queue_name,
        process_messages, delete_message, run_once=False):
    """
    Will loop indefinetly to keep polling messages
    from queue and send the message to process_message()
    if the message has content and delete the message
    to avoid multiple handeling processes of the same message.
    """
    queue = resource.meta.client.create_queue(QueueName=queue_name)

    while True:
        messages = resource.meta.client.receive_message(
            QueueUrl=queue.get("QueueUrl"),
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )
        if 'Messages' in messages:
            receipthandle = process_messages(messages)
            delete_message(create_sqs_resource(), queue, receipthandle)
        if run_once:
            break


def publish_sns(resource, topicarn, message):
    """
    Will publish the callback message containing
    status of done job to SNS Topic. This exception
    sis not handled in this version as if this fails
    there is no way for service to contact job initiator.
    """
    try:
        resource.meta.client.publish(
            TopicArn=topicarn,
            Message=message
        )

    except ClientError as e:
        if e.response["Error"]["Code"] == "NotFound":
            raise


def delete_message(resource, queue, ReceiptHandle):
    """
    Deletes a message from queue to avoid handling same message twice.
    """
    resource.meta.client.delete_message(
        QueueUrl=queue.get("QueueUrl"),
        ReceiptHandle=ReceiptHandle
        )
