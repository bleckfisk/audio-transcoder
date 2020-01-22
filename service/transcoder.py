import io
import os
from pydub import AudioSegment
from clients import s3_c
from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError


def get_file(data):

    object_name = data["file"]
    bucket_name = data["bucket"]
    try:
        response_object = s3_c.get_object(Bucket=bucket_name, Key=object_name)
        file_content = response_object["Body"].read()
        return file_content
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            raise
        if e.response["Error"]["Code"] == "NoSuchKey":
            raise KeyError


def transcode(file_content, output):
    print("started converting...")

    file_name = output['file']
    file_type = output['type']
    bucket_name = output['bucket']

    # make a file handeler from downloaded content
    handle = io.BytesIO(file_content)

    # make audiosegment from pydub and convert to flac
    audiosegment = AudioSegment.from_file(handle)
    audiosegment.export(file_name, format=file_type)

    # after converted, upload to s3
    try:
        upload_converted(file_name, bucket_name)
    except S3UploadFailedError:
        remove_local_files(file_name)
        raise
    # after upload to s3, remove
    remove_local_files(file_name)


def upload_converted(file_name, bucket_name):
    s3_c.upload_file(file_name, bucket_name, f"flacs/{file_name}")


def remove_local_files(file_name):
    print(F"REMOVING {file_name} FROM OS")
    os.remove(file_name)
