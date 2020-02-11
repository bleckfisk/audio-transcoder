from pydub import AudioSegment
import os
from pydub.utils import mediainfo
from unittest import mock
from service.core import process_message
from service.aws_boto3 import (
    listen_sqs_queue,
    create_s3_resource,
    create_sqs_resource,
    delete_message
)

from service.settings import (
    AWS_SQS_QUEUE_NAME
)

"""
These two functions will run the process with created data from
conftest.py and assert that we have called the publish_sns function.

That both tests passes is proof that even if exceptions are raised in
the process, we are still calling the publish_sns function and therefore
letting initiator know what went wrong.
"""


@mock.patch("service.core.publish_sns")
def test_service(mock_publish_sns, setup_no_exceptions):
    listen_sqs_queue(
        create_sqs_resource(),
        AWS_SQS_QUEUE_NAME,
        process_message,
        delete_message,
        True
    )

    wav_directory = setup_no_exceptions[0]
    data = setup_no_exceptions[1]

    sound = AudioSegment.from_file(wav_directory)

    for target in data:

        create_s3_resource().meta.client.download_file(
            target["bucket"],
            target["key"],
            target["key"]
            )

        sound_2 = AudioSegment.from_file(target["key"])

        info = mediainfo(target["key"])
        wav_info = mediainfo(wav_directory)

        assert info["format_name"].upper() == target["format"].upper()
        assert info["sample_rate"] == wav_info["sample_rate"]
        assert info["channels"] == wav_info["channels"]
        assert len(sound) == len(sound_2)

        os.remove(target["key"])

        assert mock_publish_sns.call_count == 1


@mock.patch("service.core.publish_sns")
def test_service_fails_callback_still_runs(mock_publish_sns, setup_error):
    """
    The set_error fixture sets up a context of trying to transcode a pdf file.
    This will not succeed and the code will handle the exception thrown
    by pydub accordingly, resulting in calling SNS with an error.

    This test proves that the SNS call is executed even if
    exceptions are thrown in the middle of the program.
    """

    listen_sqs_queue(
        create_sqs_resource(),
        AWS_SQS_QUEUE_NAME,
        process_message,
        delete_message,
        True
    )

    assert mock_publish_sns.call_count == 1
