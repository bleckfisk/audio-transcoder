
def validate_message(data):
    validations = [
        validate_message_keys(data),
        validate_input_keys(data["input"]),
        validate_output_keys(data["output"])
        ]

    return False not in validations


def validate_message_keys(body):
    return list(body.keys()) == ["input", "output"]


def validate_input_keys(input):
    return list(input.keys()) == ["file_name", "file_type", "bucket"]


def validate_output_keys(output):
    return list(output.keys()) == ["file_name", "file_type", "bucket"]


def check_type(filetype):
    # takes filetype as param and returns true if it's the correct one
    return filetype == "wav"
