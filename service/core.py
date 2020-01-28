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
    print("processing message...")
    # acceps a response checks the format of the message
    # should call check_type() and other validation functions
    message = json.loads(messages['Messages'][0]['Body'])

    if not validate_message(message):
        raise Exception(f"Invalid Message: {message}")

    file = download(create_s3_resource(), message["input"])
    transcoded_file_name = transcode(file, message["output"])

    try:
        upload(create_s3_resource(), transcoded_file_name, message["output"])
        errors_exists = False
    except Exception as e:
        errors_exists = True
        error = e

    callback(
        message["output"]["file_name"],
        message["input"]["file_type"],
        message["output"]["file_type"],
        "error" if errors_exists else "success",
        error if errors_exists else None
    )

    remove_local_files(transcoded_file_name)


def upload(resource, transcoded_file_name, output):
    # upload converted to output["bucket"]
    bucket = output["bucket"]
    object_name = f"{output['file_type']}s/{output['file_name']}"

    resource.meta.client.upload_file(
        Filename=transcoded_file_name,
        Bucket=bucket,
        Key=object_name,
    )


def remove_local_files(file):
    print(F"REMOVING {file} FROM OS")
    os.remove(file)


def download(resource, input):
    # connect to input["bucket"] and download input["file_name"]
    bucket_name = input['bucket']
    file_name = input['file_name']

    file_object = resource.meta.client.get_object(
        Bucket=bucket_name,
        Key=file_name
    )

    file = file_object["Body"].read()

    # make a file handeler from downloaded content
    tempFile = io.BytesIO(file)
    # handle the file and return it
    print("successfully downloaded, returning file now")
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

    print("Successfully published to sns")
