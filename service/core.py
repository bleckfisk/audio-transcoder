
from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError

import time
import json

from settings import (
    AWS_SQS_QUEUE_NAME,
    AWS_SNS_TOPIC_ARN,
    SLEEP_TIMER
)

from clients import (
    sqs_r,
    sqs_c,
    sns_c,
)

from validators import (
    check_message_structure,
    check_type
)

from transcoder import (
    get_file,
    transcode
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
        transcode(file_content, data["output"])
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


if __name__ == '__main__':
    main()
