
from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError

import time
import json
import io
import os

from settings import (
    AWS_SQS_QUEUE_NAME,
    AWS_SNS_TOPIC_ARN,
    SLEEP_TIMER
)

from pydub import AudioSegment

from clients import (
    sqs_r,
    sqs_c,
    sns_c,
    s3_c
)

from validators import (
    check_message_structure,
    check_type
)


def retry(SLEEP_TIMER):
    time.sleep(SLEEP_TIMER)
    main()


def main():
    try:
        global queue
        queue = get_queue()
    except ClientError:
        print(f"Queue not found. Retrying in {SLEEP_TIMER}")
        retry(SLEEP_TIMER)

    try:
        global messages
        messages = get_messages(queue)
    except KeyError:
        print(f"No Message was found, retrying in {SLEEP_TIMER}")
        retry(SLEEP_TIMER)

    try:
        global data
        data = process_messages(messages)
    except KeyError:
        print(f"The input structure is unsupported, retrying in {SLEEP_TIMER}")
        retry(SLEEP_TIMER)

    try:
        global file_content
        file_content = get_file(data["input"])
    except ClientError:
        print("The bucket was not found")
        retry(SLEEP_TIMER)
    except KeyError:
        print("The file was not found in given bucket.")
        retry(SLEEP_TIMER)

    try:
        process(file_content, data["output"])
    except S3UploadFailedError:
        print("Upload failed, target bucket not found")
        retry(SLEEP_TIMER)

    try:
        notify_sns()
        print("successfully notified SNS")
    except ClientError:
        print("The given topic arn was not found.")
        retry(SLEEP_TIMER)


def get_queue():
    try:
        return sqs_r.get_queue_by_name(QueueName=AWS_SQS_QUEUE_NAME) 
    except ClientError as e:
        if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
            raise


def get_messages(queue):
    try:
        response = sqs_c.receive_message(
            QueueUrl=queue.url,
            MaxNumberOfMessages=5,
            VisibilityTimeout=123,
            WaitTimeSeconds=0,
        )
        if "Messages" in response:
            return response["Messages"]
        else:
            raise KeyError
    except KeyError:
        raise


def process_messages(messages):
    print("processing...")
    # acceps a response checks the format of the message
    # should call check_type() and other validation functions
    data = json.loads(messages[0]['Body'])
    try:
        approved_structure = check_message_structure(data)
        if not approved_structure:
            raise TypeError('The data structure in message is not supported')

        approved_filetype = check_type(data['input']['type'])
        if not approved_filetype:
            raise TypeError('File format not supported')

        if approved_structure and approved_filetype:
            return data

    except TypeError:
        raise


def get_file(data):

    object_name = data["file"]
    bucket_name = data["bucket"]
    try:
        response_object = s3_c.get_object(Bucket=bucket_name, Key=object_name)
        file_content = response_object["Body"].read()
        return file_content
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            raise
        if e.response["Error"]["Code"] == "NoSuchKey":
            raise KeyError


def process(file_content, output):
    print("started converting...")

    file_name = output['file']
    file_type = output['type']
    bucket_name = output['bucket']

    # make a file handeler from downloaded content
    handle = io.BytesIO(file_content)

    # make audiosegment from pydub and convert to flac
    audiosegment = AudioSegment.from_file(handle)
    audiosegment.export(file_name, format=file_type)

    # after converted, upload to s3
    try:
        upload_converted(file_name, bucket_name)
    except S3UploadFailedError:
        remove_local_files(file_name)
        raise
    # after upload to s3, remove
    remove_local_files(file_name)


def upload_converted(file_name, bucket_name):

    s3_c.upload_file(file_name, bucket_name, f"flacs/{file_name}")


def notify_sns():
    # publish notification to topic
    try:
        sns_c.publish(
            TopicArn=AWS_SNS_TOPIC_ARN,
            Message="SUCCESS!!!!"
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "NotFound":
            raise


def remove_local_files(file_name):
    print(F"REMOVING {file_name} FROM OS")
    os.remove(file_name)


if __name__ == '__main__':
    main()
