import io
import os
import json
from botocore.exceptions import ClientError

from .validators import (
    validate_message,
    check_error_list,
    validate_input_format,
    validate_output_formats
)

from .aws_boto3 import create_s3_resource, create_sns_resource, publish_sns
from .loggers import AWS_Logger, Service_Logger
from .settings import (
    RESPONSE_TOPIC_ARN
)
from .transcoder import transcode
from .helpers import get_format


def process_message(message):
    """
    Function for handling the core functionality of the service.
    Validates the message, download file, transcode and upload file again
    based on inputs from SQS. Exceptions raised contribute to the errors-list
    which later is used in the callback to SNS Topic.
    """

    errors = []

    if not validate_message(message):
        raise Exception(f"Invalid Message: {message}")

    file_name = download(create_s3_resource(), message["input"])
    format = get_format(file_name)

    if not validate_input_format(format):
        raise Exception(f'Invalid Input Format: {format}')

    for output in message["outputs"]:
        if not validate_output_formats(output["format"]):
            raise Exception(f'Invalid Output Format: {output["format"]}')

        try:
            transcoded = transcode(file_name, output)
            upload(create_s3_resource(), transcoded, output)
        except ClientError as e:
            errors.append(e.response["Error"]["Message"])
            AWS_Logger.exception(e)

        except Exception as e:
            """Unforseen exceptions should not break the process,
            instead tell SNS that an unexted error occured"""

            msg = "Unexpected Error."
            errors.append(msg)
            Service_Logger.exception(e)

    callback(
        message["id"],
        RESPONSE_TOPIC_ARN,
        "error" if check_error_list(errors) else "success",
        errors if check_error_list(errors) else None
    )

    remove_file(file_name)


def upload(resource, transcoded, output):
    """takes the converted file and uploads it to s3"""
    bucket = output["bucket"]
    key = output["key"]

    file = io.BytesIO(transcoded.read())

    resource.meta.client.upload_fileobj(
        file,
        Bucket=bucket,
        Key=key,
    )


def download(resource, input):
    """downloads the file specified in input and
    returns the name of the file as a string"""
    bucket_name = input['bucket']
    file_name = input['key']

    resource.meta.client.download_file(
        bucket_name,
        file_name,
        file_name
    )

    return file_name


def callback(id, topic_arn, status, errors=None):
    """takes the summary of the job and publishes it to SNS"""
    publish_sns(
        create_sns_resource(),
        topic_arn,
        json.dumps(
            {
                "id": id,
                "status": status,
                "errors": errors
            }
            )
        )


def remove_file(file_name):
    os.remove(file_name)
