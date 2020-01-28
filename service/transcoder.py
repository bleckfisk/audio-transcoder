from pydub import AudioSegment


def transcode(file, output):
    print("started converting...")
    file_name = output['file']
    file_type = output['type']

    # make audiosegment from pydub and convert to flac
    audiosegment = AudioSegment.from_file(file)
    converted = audiosegment.export(file_name, format=file_type)
    return converted


def upload_converted(resource, file_name, bucket_name):
    resource.meta.client.upload_file(
        file_name,
        bucket_name,
        f"flacs/{file_name}")
