import io
from service.core import upload, download
from uuid import uuid4
from service.aws_boto3 import create_s3_resource


def test_download(s3_bucket):

    """
    Tests proves that subject returned from download() contains the
    same data that we uploaded manually.
    """

    key = str(uuid4())
    body = b"testdata"
    bucket = s3_bucket.name
    s3_bucket.put_object(Key=key, Body=body)

    payload = {
        "key": key,
        "bucket": bucket
    }

    subject = download(create_s3_resource(), payload)

    assert subject.read() == body


def test_upload(s3_bucket):
    """
    Test proves that file created here and sent to
    upload() is uploaded accordingly.
    """

    key = str(uuid4())
    bucket = s3_bucket.name

    payload = {
        "key": key,
        "bucket": bucket
    }

    some_data = b"test123"
    file_to_upload = io.BytesIO(some_data)

    upload(create_s3_resource(), file_to_upload, payload)

    my_bucket_objects = s3_bucket.objects.all()

    for obj in my_bucket_objects:
        assert obj.key == key


def test_upload_download_data_assertion(s3_bucket):

    key = str(uuid4())
    bucket = s3_bucket.name

    payload = {
        "key": key,
        "bucket": bucket
    }

    some_data = b"test123"
    file_to_upload = io.BytesIO()
    file_to_upload.write(some_data)

    upload(create_s3_resource(), file_to_upload, payload)

    my_bucket_objects = s3_bucket.objects.all()

    for obj in my_bucket_objects:
        assert obj.key == key

    downloaded = download(create_s3_resource(), payload)

    assert downloaded.read() == file_to_upload.read()

