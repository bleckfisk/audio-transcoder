import pytest
import os
from service.transcoder import transcode


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
