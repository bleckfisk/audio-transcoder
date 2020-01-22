from botocore.exceptions import ClientError
from clients import (
    sqs_c,
    sqs_r,
    sns_c
)

from settings import (
    AWS_SQS_QUEUE_NAME,
    AWS_SNS_TOPIC_ARN
)


def get_queue():
    try:
        return sqs_r.get_queue_by_name(QueueName=AWS_SQS_QUEUE_NAME) 
    except ClientError as e:
        if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
            raise


def get_messages(queue):
    try:
        response = sqs_c.receive_message(
            QueueUrl=queue.url,
            MaxNumberOfMessages=5,
            VisibilityTimeout=123,
            WaitTimeSeconds=0,
        )
        if "Messages" in response:
            return response["Messages"]
        else:
            raise KeyError
    except KeyError:
        raise


def notify_sns():
    # publish notification to topic
    try:
        sns_c.publish(
            TopicArn=AWS_SNS_TOPIC_ARN,
            Message="SUCCESS!!!!"
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "NotFound":
            raise

