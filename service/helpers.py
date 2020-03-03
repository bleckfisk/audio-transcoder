from pydub.utils import mediainfo

"""
This file is for helper functions that should
provide cleaner code out in the actual process.
Currently only contains one function but
exists for a long term maintainability.
"""


def get_format(file_name):
    """
    accepts a file name string that has to exist on the system,
    checks the file format type and returns the format as a string.

    Used for validating formats through validators.py
    """
    info = mediainfo(file_name)
    return info["format_name"].upper()
