import boto3
from botocore.exceptions import DataNotFoundError
import time
import json
import io
import os

from settings import (
    AWS_SQS_ENDPOINT_URL,
    AWS_S3_ENDPOINT_URL,
    AWS_SNS_ENDPOINT_URL,
    AWS_DEFAULT_REGION,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    GCP_ENCODED_CREDENTIALS,
    SENTRY_ID,
    SENTRY_KEY,
)

from pydub import AudioSegment


def check_sqs():

    sqs_r = boto3.resource('sqs', endpoint_url=AWS_SQS_ENDPOINT_URL)
    sqs_c = boto3.client('sqs', endpoint_url=AWS_SQS_ENDPOINT_URL)

    try:
        queue = sqs_r.get_queue_by_name(QueueName="testqueue")
    except Exception:
        print("no queue yet...")
        time.sleep(10)
        check_sqs()

    try:
        response = sqs_c.receive_message(
            QueueUrl=queue.url,
            MaxNumberOfMessages=5,
            VisibilityTimeout=123,
            WaitTimeSeconds=0,
        )
        
        if not response["Messages"]:
            raise Exception("Queue found, but no messages...")

    except Exception:
        print("no response yet...")
        time.sleep(10)
        check_sqs()

    process_messages(response)


def process_messages(response):
    print("processing...")
    # acceps a response checks the format of the message
    # should call check_type() and other validation functions
    data = json.loads(response['Messages'][0]['Body'])

    approved_structure = check_message_structure(data)
    if not approved_structure:
        raise TypeError('The data structure in message is not supported')

    approved_filetype = check_type(data['input']['type'])
    if not approved_filetype:
        raise TypeError('The file type is not supported. Please provide .wav format.')

    file_content = get_file(data['input'])
    convert(file_content, data['output'])


def check_message_structure(body):
    #
    # REWORK THIS!!!!
    #
    if isinstance(body["input"], dict):
        if isinstance(body["input"]["file"], str):
            if isinstance(body["input"]["type"], str):
                if isinstance(body["output"], dict):
                    if isinstance(body["output"]["file"], str):
                        if isinstance(body["output"]["type"], str):
                            return True
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False


def check_type(filetype):
    # takes filetype as param and returns true if it's the correct one
    return filetype == ".wav"


def get_file(data):

    s3_c = boto3.client('s3', endpoint_url=AWS_S3_ENDPOINT_URL)

    bucket = "testbucket"

    object_name = data["file"]

    # file_name = data["file"] + data["type"]

    try:
        response_object = s3_c.get_object(Bucket=bucket, Key=object_name)
        file_content = response_object["Body"].read()
    except DataNotFoundError:
        print("Data not found")

    return file_content


def convert(file_content, output):
    print("started converting...")

    # make a file handeler from downloaded content
    handle = io.BytesIO(file_content)

    # make audiosegment from pydub and convert to flac
    audiosegment = AudioSegment.from_file(handle)
    audiosegment.export("exported.flac", format="flac")

    # after converted, upload to s3

    # after upload to s3, remove
    os.remove("exported.flac")


if __name__ == '__main__':

    check_sqs()
