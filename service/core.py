import os
import io
import json
from .validators import validate_message, check_error_list as errorcheck
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

    errors = []

    for output in message["outputs"]:
        file = download(create_s3_resource(), message["input"])
        transcode(file, output)

        try:
            upload(create_s3_resource(), output)
        except Exception as e:
            errors.append(e)

    callback(
        message["input"],
        message["outputs"],
        "error" if errorcheck(errors) else "success",
        errors if errorcheck(errors) else None
    )

    for output in message["outputs"]:
        remove_local_files(output["key"])

    return messages['Messages'][0]['ReceiptHandle']


def upload(resource, output):
    # upload converted to output["bucket"]
    bucket = output["bucket"]
    key = output["key"]

    resource.meta.client.upload_file(
        Filename=key,
        Bucket=bucket,
        Key=key,
    )


def remove_local_files(file):
    print(F"REMOVING {file} FROM OS")
    os.remove(file)


def download(resource, input):
    # connect to input["bucket"] and download input["file_name"]
    bucket_name = input['bucket']
    file_name = input['key']

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


def callback(input, outputs, status, errors=None):

    publish_sns(
        create_sns_resource(),
        AWS_SNS_TOPIC_ARN,
        json.dumps(
            {
                "from_type": input,
                "to_type": outputs,
                "status": status,
                "errors": errors,
            }
        ),
    )

    print("Successfully published to sns")
