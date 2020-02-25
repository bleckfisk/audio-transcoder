from . import aws_boto3
from .settings import REQUEST_QUEUE_NAME
from .core import process_message

aws_boto3.listen_sqs_queue(
    aws_boto3.create_sqs_resource(),
    REQUEST_QUEUE_NAME,
    process_message
)
