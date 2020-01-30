import io
import json
from pydub.audio_segment.exceptions import CouldntDecodeError
from botocore.exceptions import ClientError
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
        try:
            file = download(create_s3_resource(), message["input"])
            transcoded = transcode(file, output)
            upload(create_s3_resource(), transcoded, output)
        except ClientError as e:
            print(e)
            errors.append(e)

        except CouldntDecodeError:
            msg = "Coudln't decode due to bad format or corrupt data."
            print(msg)
            errors.append(msg)

        except IndexError:
            msg = "Unsupported format."
            print(msg)
            errors.append(msg)

        except Exception:
            msg = "Unsupported format."
            print(msg)
            errors.append(msg)

    callback(
        AWS_SNS_TOPIC_ARN,
        message["input"],
        message["outputs"],
        "error" if errorcheck(errors) else "success",
        errors if errorcheck(errors) else None
    )

    return messages['Messages'][0]['ReceiptHandle']


def upload(resource, transcoded, output):
    # upload converted to output["bucket"]
    bucket = output["bucket"]
    key = output["key"]

    file = io.BytesIO(transcoded.read())

    resource.meta.client.upload_fileobj(
        file,
        Bucket=bucket,
        Key=key,
    )


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


def callback(topic_arn, input, outputs, status, errors=None):

    publish_sns(
        create_sns_resource(),
        topic_arn,
        json.dumps(
            {
                "from": input,
                "to": outputs,
                "status": status,
                "errors": errors,
            }
        ),
    )

    print("Successfully published to sns")
