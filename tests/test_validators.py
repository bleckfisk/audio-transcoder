from uuid import uuid4
from service.validators import (
    check_error_list,
    validate_message,
    validate_message_keys,
    validate_input_keys,
    validate_output_keys
)


"""
Tests in this file proves that validators in validators.py returns correct
boolean depending on payload key names.
"""


def test_check_error_list():
    empty = []
    assert check_error_list(empty) is False

    not_empty = ["test", "test2"]
    assert check_error_list(not_empty) is True


def test_validate_message_keys():

    payload = {
        "input": {
            "key": str(uuid4()),
            "bucket": str(uuid4())
        },
        "outputs": [
            {
                "key": str(uuid4()),
                "format": str(uuid4()),
                "bucket": str(uuid4())
            },
            {
                "key": str(uuid4()),
                "format": str(uuid4()),
                "bucket": str(uuid4())
            }
        ]
    }

    assert validate_message_keys(payload) is True


def test_validate_message_keys_returns_false():

    payload = {
        "question": {
            "key": str(uuid4()),
            "bucket": str(uuid4())
        },
        "wanted": [
            {
                "format": str(uuid4()),
                "key": str(uuid4()),
                "bucket": str(uuid4())
            },
            {
                "key": str(uuid4()),
                "format": str(uuid4()),
                "bucket": str(uuid4())
            }
        ]
    }

    assert validate_message_keys(payload) is False


def test_validate_input_keys():

    payload = {
        "input": {
            "key": str(uuid4()),
            "bucket": str(uuid4())
        },
        "outputs": [
            {
                "key": str(uuid4()),
                "format": str(uuid4()),
                "bucket": str(uuid4())
            },
            {
                "key": str(uuid4()),
                "format": str(uuid4()),
                "bucket": str(uuid4())
            }
        ]
    }

    assert validate_input_keys(payload["input"]) is True


def test_validate_input_keys_returns_false():

    payload = {
        "input": {
            "song_id": str(uuid4()),
            "s3": str(uuid4())
        },
        "outputs": [
            {
                "key": str(uuid4()),
                "format": str(uuid4()),
                "bucket": str(uuid4())
            },
            {
                "key": str(uuid4()),
                "format": str(uuid4()),
                "bucket": str(uuid4())
            }
        ]
    }

    assert validate_input_keys(payload["input"]) is False


def test_validate_output_keys():

    payload = {
        "input": {
            "key": str(uuid4()),
            "bucket": str(uuid4())
        },
        "outputs": [
            {
                "key": str(uuid4()),
                "format": str(uuid4()),
                "bucket": str(uuid4())
            },
            {
                "key": str(uuid4()),
                "format": str(uuid4()),
                "bucket": str(uuid4())
            }
        ]
    }
    assert validate_output_keys(payload["outputs"]) is True


def test_validate_output_keys_returs_false():

    payload = {
        "input": {
            "key": str(uuid4()),
            "bucket": str(uuid4())
        },
        "outputs": [
            {
                "key": str(uuid4()),
                "type": str(uuid4()),
                "bucket": str(uuid4())
            },
            {
                "key": str(uuid4()),
                "format": str(uuid4()),
                "s3": str(uuid4())
            }
        ]
    }
    assert validate_output_keys(payload["outputs"]) is False


def test_validate_message():

    payload = {
        "input": {
            "key": str(uuid4()),
            "bucket": str(uuid4())
        },
        "outputs": [
            {
                "key": str(uuid4()),
                "format": str(uuid4()),
                "bucket": str(uuid4())
            },
            {
                "key": str(uuid4()),
                "format": str(uuid4()),
                "bucket": str(uuid4())
            }
        ]
    }

    assert validate_message(payload) is True
