import boto3
from botocore.exceptions import DataNotFoundError
import time
import json
from pydub import AudioSegment


def check_sqs():

    sqs_r = boto3.resource('sqs', endpoint_url="http://localstack:5000")
    sqs_c = boto3.client('sqs', endpoint_url="http://localstack:5000")

    try:
        queue = sqs_r.get_queue_by_name(QueueName="testqueue")
        response = sqs_c.receive_message(
            QueueUrl=queue.url,
            MaxNumberOfMessages=5,
            VisibilityTimeout=123,
            WaitTimeSeconds=0,
        )
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

    sound = download_file(data['input'])
    convert(sound, data['output'])


def check_message_structure(body):
    for object in body:
        if not isinstance(object, dict):
            return False
        else:
            for data in object:
                if not isinstance(data, str):
                    return False
                else:
                    return True



def check_type(filetype):
    # takes filetype as param and returns true if it's the correct one
    return filetype == ".wav"


def download_file(data):

    s3_c = boto3.client('s3', endpoint_url="http://localstack:5001")

    try:
        sound = s3_c.download_file(
            'testbucket',
            f"{data['file']}",
            f"{data['file']}{data['type']}"
            )
    except DataNotFoundError:
        print("Data not found")

    return sound


def convert(sound, output):
    print("started converting...")
    print(sound)
    print(output)


if __name__ == '__main__':

    check_sqs()
