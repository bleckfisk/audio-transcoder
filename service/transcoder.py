from pydub import AudioSegment


def transcode(file, output):

    key = output['key']
    format = output['format']

    # make audiosegment from pydub and convert to flac
    audiosegment = AudioSegment.from_file(file)
    audiosegment.export(key, format=format)
