import io
from pydub import AudioSegment


def transcode(file, output):

    format = output['format']
    handle = io.BytesIO()

    # make audiosegment from pydub and convert to flac
    audio = AudioSegment.from_file(file)
    audio.export(handle, format=format)

    return handle
