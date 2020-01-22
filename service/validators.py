
"""
Validators to check the input data is correct data types.

NOTE TO SELF:
There are better ways to do this.
Figure it out in time.

"""


def check_message_structure(body):
    """
    Body should contain two dictionaries, containing keys with strings in them.
    Return true if they are.
    """
    if check_input_structure(body["input"]):
        if check_output_structure(body["output"]):
            return True
        else:
            return False
    else:
        return False


def check_input_structure(input):
    if isinstance(input, dict):
        if isinstance(input["type"], str):
            if isinstance(input["file"], str):
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def check_output_structure(output):
    if isinstance(output, dict):
        if isinstance(output["type"], str):
            if isinstance(output["file"], str):
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def check_type(filetype):
    # takes filetype as param and returns true if it's the correct one
    return filetype == "wav"
