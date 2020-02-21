import pytest
import os
from service.transcoder import transcode
from unittest import mock
from pydub.exceptions import CouldntDecodeError, CouldntEncodeError


def test_all_supported_testfiles(list_of_supported_files):

    """
    Tests that asserts that an exception is thrown for each supported file
    to prove that they in fact are supported.
    """

    output = {
        "key": "not-used-in-this-function",
        "format": "mp3",
        "bucket": "not-used-in-this-function"
    }

    for file in list_of_supported_files:
        with open(
            f"{os.getcwd()}/tests/test_samples/supported/{file}", "rb"
                ) as f:

            transcode(f, output)


@mock.patch('service.loggers.Service_Logger')
def test_all_unsupported_testfiles(mock_Logger, list_of_unsupported_files):

    """
    Tests that asserts that an exception is thrown for each unsupported file
    to prove that they in fact are unsupported.
    """

    output = {
        "key": "not-used-in-this-function",
        "format": "mp3",
        "bucket": "not-used-in-this-function"
    }

    for file in list_of_unsupported_files:
        with open(
            f"{os.getcwd()}/tests/test_samples/unsupported/{file}", "rb"
                ) as f:

            with pytest.raises((
                    CouldntDecodeError,
                    IndexError,
                    KeyError
                    )):

                transcode(f, output)


@mock.patch('service.loggers.Service_Logger')
def test_supported_input_bad_output(mock_Logger):
    """
    This test tests that CouldntEncodeError is thrown when trying to export
    a file format not supported, while the input is supported.
    Sound to video for example.
    """

    output = {
        "key": "not-used-in-this-function",
        "format": "m4a",
        "bucket": "not-used-in-this-function"
    }

    with open(
        f"{os.getcwd()}/tests/test_samples/supported/sound.wav", "rb"
            ) as f:

        with pytest.raises(CouldntEncodeError):
            transcode(f, output)
