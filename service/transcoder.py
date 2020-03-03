import io
from pydub import AudioSegment


def transcode(file_name, output):
    """
    Takes a file and a part of the message object as arguments
    and uses it as instructions for how the transcoding should be done.
    Transcodes and Returns a bytesIO-object to
    be handled later by upload() function.
    """
    format = output['format'].upper()
    handle = io.BytesIO()
    audio = AudioSegment.from_file(file_name)
    audio.export(handle, format=format)
    return handle
