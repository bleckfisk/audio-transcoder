
from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError
import time
import json
from settings import SLEEP_TIMER

from validators import (
    check_message_structure,
    check_type
)

from transcoder import (
    get_file,
    transcode
)

from aws_boto3 import (
    get_queue,
    get_messages,
    notify_sns
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


if __name__ == '__main__':
    main()
