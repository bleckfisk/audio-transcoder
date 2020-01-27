from service.validators import (
    check_input_structure,
    check_output_structure,
    check_message_structure,
    check_type,
)


def test_check_type_with_wav():
    correct_input = "wav"
    assert check_type(correct_input) is True


def test_check_type_not_wav():
    not_wav = 'mp3'
    assert check_type(not_wav) is False


def test_check_input_structure_correct_input():
    correct_input = {
        "file": "string",
        "type": "string"
    }
    assert check_input_structure(correct_input) is True


def test_check_input_structure_bad_input():

    bad_input = {
        "file": 123,
        "type": "string"
    }

    bad_input_2 = {
        "file": "string",
        "type": {
            "dictionary": "not string"
        }
    }

    assert check_input_structure(bad_input) is False
    assert check_input_structure(bad_input_2) is False


def test_check_output_structure_correct_output():
    correct_output = {
        "file": "string",
        "type": "string"
    }
    assert check_output_structure(correct_output) is True


def test_check_output_structure_bad_output():

    bad_output = {
        "file": 123,
        "type": "string"
    }

    bad_output_2 = {
        "file": "string",
        "type": {
            "dictionary": "not string"
        }
    }

    assert check_input_structure(bad_output) is False
    assert check_input_structure(bad_output_2) is False


def test_check_message_structure():
    correct_structure = {
        "input": {
            "file": "something",
            "type": "a type",
            "bucket": "a bucket name"
        },
        "output": {
            "file": "a target file name",
            "type": "a target type format",
            "bucket": "a target bucket name"
        }
    }

    bad_structure = {
        "input": {
            "file": "something",
            "type": "a type",
            "bucket": "a bucket name"
        },
        "output": {
            "file": ["string", 123],
            "type": 0,
            "bucket": "a target bucket name"
        }
    }

    bad_structure_2 = {
        "input": {
            "file": {
                "name": "something",
                "writer": "someone"
            },
            "type": "a type",
            "bucket": {
                "https": True,
                "url": "https://ilikeit.example"
            }
        },
        "output": {
            "file": "a target file name",
            "type": "a target type format",
            "bucket": "a target bucket name"
        }
    }

    assert check_message_structure(correct_structure) is True
    assert check_message_structure(bad_structure) is False
    assert check_message_structure(bad_structure_2) is False
