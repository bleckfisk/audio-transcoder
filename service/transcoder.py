from pydub import AudioSegment


def transcode(file, output):
    print("started converting...")
    print(output['key'])
    key = output['key']
    format = output['format']

    # make audiosegment from pydub and convert to flac
    audiosegment = AudioSegment.from_file(file)
    audiosegment.export(key, format=format)
