from pydub.utils import mediainfo


def get_format(file_name):
    info = mediainfo(file_name)
    return info["format_name"].upper()
