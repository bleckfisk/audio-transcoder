import io
import json
from pydub.exceptions import CouldntDecodeError, CouldntEncodeError
from botocore.exceptions import ClientError
from .validators import validate_message, check_error_list
from .aws_boto3 import create_s3_resource, create_sns_resource, publish_sns
from .loggers import AWS_Logger, Service_Logger
from .settings import (
    AWS_SNS_TOPIC_ARN
)
from .transcoder import transcode


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

    for output in message["outputs"]:
        try:
            file = download(create_s3_resource(), message["input"])
            transcoded = transcode(file, output)
            upload(create_s3_resource(), transcoded, output)
        except ClientError as e:
            errors.append(e.response["Error"]["Message"])
            AWS_Logger.exception(e)

        except CouldntDecodeError as e:
            msg = "Coudln't decode due to bad format or corrupt data."
            errors.append(msg)
            Service_Logger.exception(e)

        except CouldntEncodeError as e:
            msg = "Coudln't encode asked format due to incompatibility."
            errors.append(msg)
            Service_Logger.exception(e)

        except IndexError as e:
            msg = "Transcoding could not start. Format not found."
            errors.append(msg)
            Service_Logger.exception(e)

        except KeyError as e:
            msg = "Transcoding could not start. Format not found."
            errors.append(msg)
            Service_Logger.exception(e)

        except Exception as e:
            """Unforseen exceptions should not break the process,
            instead tell SNS that an unexted error occured"""

            msg = "Unexpected Error."
            errors.append(msg)
            Service_Logger.exception(e)

    callback(
        message["id"],
        AWS_SNS_TOPIC_ARN,
        "error" if check_error_list(errors) else "success",
        errors if check_error_list(errors) else None
    )


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
    """downloads the file specified in input and return it as BytesIO object"""
    bucket_name = input['bucket']
    file_name = input['key']

    file_object = resource.meta.client.get_object(
        Bucket=bucket_name,
        Key=file_name
    )

    file = file_object["Body"].read()
    tempFile = io.BytesIO(file)
    return tempFile


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
