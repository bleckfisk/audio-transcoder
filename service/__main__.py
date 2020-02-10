from . import aws_boto3
from .settings import AWS_SQS_QUEUE_NAME
from .core import process_message
from .aws_boto3 import delete_message

aws_boto3.listen_sqs_queue(
    aws_boto3.create_sqs_resource(),
    AWS_SQS_QUEUE_NAME,
    process_message,
    delete_message
)
