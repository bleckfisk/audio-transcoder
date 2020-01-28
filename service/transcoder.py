from pydub import AudioSegment


def transcode(file, output):
    print("started converting...")
    file_name = f"{output['file_name']}.{output['file_type']}"
    file_type = output['file_type']

    # make audiosegment from pydub and convert to flac
    audiosegment = AudioSegment.from_file(file)
    audiosegment.export(
        file_name,
        format=file_type
        )

    return file_name


"""
def upload_converted(resource, file_name, bucket_name):
    resource.meta.client.upload_file(
        file_name,
        bucket_name,
        f"flacs/{file_name}")
"""
