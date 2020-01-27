import io
import os
from pydub import AudioSegment
from clients import s3_c
from boto3.exceptions import S3UploadFailedError


def transcode(file, output):
    print("started converting...")
    file_name = output['file']
    file_type = output['type']

    # make audiosegment from pydub and convert to flac
    audiosegment = AudioSegment.from_file(file)
    converted = audiosegment.export(file_name, format=file_type)
    return converted


def upload_converted(file_name, bucket_name):
    s3_c.upload_file(file_name, bucket_name, f"flacs/{file_name}")


