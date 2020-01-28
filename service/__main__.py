from . import aws_boto3
from .settings import AWS_SQS_QUEUE_NAME
from .core import process_messages


aws_boto3.listen_sqs_queue(
    aws_boto3.create_sqs_resource(),
    AWS_SQS_QUEUE_NAME,
    process_messages
)
