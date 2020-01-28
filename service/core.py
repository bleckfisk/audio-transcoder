import os
import io
import json
from .validators import validate_message
from .aws_boto3 import create_s3_resource, create_sns_resource, publish_sns
from .settings import (
    AWS_SNS_TOPIC_ARN
)

from .transcoder import transcode


def process_messages(messages):
    print("processing...")
    # acceps a response checks the format of the message
    # should call check_type() and other validation functions
    message = json.loads(messages[0]['Body'])

    if not validate_message(message):
        raise Exception(f"Invalid Message: {message}")

    file = download(create_s3_resource(), message["input"])
    converted = transcode(file, message["output"])

    try:
        upload(create_s3_resource(), converted, message["output"])
    except Exception as e:
        error = e
        return_code = True

    callback(
        message["output"]["file_name"],
        message["input"]["file_type"],
        message["output"]["file_type"],
        "error" if return_code else "success",
        error if return_code else None
    )


def upload(resource, converted, output):
    # upload converted to output["bucket"]

    bucket = output["bucket"]
    object_name = f"{output['file_type']}s/{output['file_name']}"
    resource.meta.client.upload_file(
        converted,
        bucket,
        object_name
    )


def remove_local_files(converted):
    print(F"REMOVING {converted} FROM OS")
    os.remove(converted)


def download(resource, input):
    # connect to input["bucket"] and download input["file_name"]
    bucket_name = input['bucket']
    file_name = input['file_name']

    file = resource.meta.client.get_object(
        Bucket=bucket_name,
        Key=file_name
    ).read()

    # make a file handeler from downloaded content
    tempFile = io.BytesIO(file)
    # handle the file and return it
    return tempFile


def callback(file_name, from_type, to_type, status, errors=None):
    publish_sns(
        create_sns_resource(),
        AWS_SNS_TOPIC_ARN,
        json.dumps(
            {
                "file_name": file_name,
                "from_type": from_type,
                "to_type": to_type,
                "status": status,
                "errors": errors,
            }
        ),
    )
