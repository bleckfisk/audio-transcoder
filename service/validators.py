"""
A file containing validator functions to make sure
the input from SQS Message is correct.

Every function follows the logic of checking the keys and
returning True or False depending on whether or not they are correct.
"""


def validate_message(data):
    try:
        validations = [
            validate_message_keys(data),
            validate_input_keys(data["input"]),
            validate_output_keys(data["outputs"])
            ]
    except KeyError:
        return False
    return False not in validations


def validate_message_keys(body):
    return list(body.keys()) == ["input", "outputs"]


def validate_input_keys(input):
    return list(input.keys()) == ["key", "bucket"]


def validate_output_keys(outputs):
    validations = []
    for output in outputs:
        validations.append(list(output.keys()) == ["key", "format", "bucket"])
    return False not in validations


def check_error_list(errors):
    return len(errors) > 0
