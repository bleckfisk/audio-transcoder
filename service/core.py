import boto3
import time
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
        process_messages(response)
    except Exception:
        print("no response yet...")
        time.sleep(10)
        check_sqs()


def process_messages(response):
    print("processing...")
    # acceps a response checks the format of the message
    # should call check_type() and other validation functions
    print(response['Messages'])


def check_type(filetype):
    # takes filetype as param and returns true if it's the correct one
    return filetype == "wav"


def convert(directory, data):
    sound = AudioSegment.from_file(
        f"{directory}/{data['input']['filename']}.{data['input']['type']}",
        format="wav"
        )

    sound.export(
        f"{directory}/{data['output']['filename']}.{data['output']['type']}",
        format='flac'
        )


if __name__ == '__main__':

    check_sqs()
