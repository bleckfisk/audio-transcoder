import pytest
import io
import os
from service.transcoder import transcode
from pydub.audio_segment import CouldntDecodeError


def test_transcode_unsupported_data(unsupported_transcode_data):
    """
    Test that proves that exceptions are raised when files with bad formats
    are passed to the transcoder. In this case we have the following data:

    handles[0] == jpg
    handles[1] == pdf

    """
    handles = unsupported_transcode_data["handles"]
    outputs = unsupported_transcode_data["outputs"]

    with pytest.raises(IndexError):
        file = io.BytesIO(handles[0].read())
        for output in outputs:
            transcode(file, output)

    with pytest.raises(CouldntDecodeError):
        file = io.BytesIO(handles[1].read())
        for output in outputs:
            transcode(file, output)


def test_transcode_supported_data(supported_transcode_data):
    """
    Test that in contrast to above does not raise exception as
    the format is supported.

    supported_transcode_data["handles"][0] = wav

    """
    file = supported_transcode_data["handles"][0]
    output = supported_transcode_data["outputs"]
    transcode(file, output)


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


def test_all_unsupported_testfiles(list_of_unsupported_files):

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

            with pytest.raises((Exception)):
                transcode(f, output)
