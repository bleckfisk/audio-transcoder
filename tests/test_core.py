import io
import pytest
from service.core import upload, download, callback
from uuid import uuid4
from service.aws_boto3 import create_s3_resource
from botocore.exceptions import ClientError
from service import settings


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


def test_download_key_not_exists(s3_bucket):

    key_1 = str(uuid4())
    key_2 = str(uuid4())

    body = b"testdata"
    bucket = s3_bucket.name
    s3_bucket.put_object(Key=key_1, Body=body)

    payload = {
        "key": key_2,
        "bucket": bucket
    }

    with pytest.raises(ClientError):
        download(create_s3_resource(), payload)


def test_download_bucket_not_exists(s3_bucket):

    key = str(uuid4())
    body = b"testdata"
    not_exists = str(uuid4())
    s3_bucket.put_object(Key=key, Body=body)

    payload = {
        "key": key,
        "bucket": not_exists
    }

    with pytest.raises(ClientError):
        download(create_s3_resource(), payload)


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


def test_upload_bucket_not_exists(s3_bucket):

    key = str(uuid4())
    bucket = str(uuid4())

    payload = {
        "key": key,
        "bucket": bucket
    }

    some_data = b"test123"
    file_to_upload = io.BytesIO(some_data)

    with pytest.raises(ClientError):
        upload(create_s3_resource(), file_to_upload, payload)


def test_upload_download_data_assertion(s3_bucket):

    """
    Test proves that after uploading a file, and downloading it again, the
    content of the file is equal and therefore data is intact.
    """

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


def test_callback_success(sns_topic_arn):
    """
    Test proves that callback() is not throwing exceptions
    when errors-argument == None
    """
    input_key = str(uuid4())
    bucket = str(uuid4())

    output_key = str(uuid4())

    input = {
        "key": input_key,
        "bucket": bucket
    }

    outputs = [
        {
            "key": output_key,
            "bucket": bucket
        }
    ]

    status = "success"

    errors = None

    callback(sns_topic_arn, input, outputs, status, errors)


def test_callback_errors(sns_topic_arn):
    """
    Test proves that callback() is not throwing exceptions
    when errors-list is passed as argument
    """
    input_key = str(uuid4())
    bucket = str(uuid4())
    output_key = str(uuid4())

    input = {
        "key": input_key,
        "bucket": bucket
    }

    outputs = [
        {
            "key": output_key,
            "bucket": bucket
        }
    ]

    status = "error"

    errors = [str(uuid4()), str(uuid4()), str(uuid4())]

    callback(sns_topic_arn, input, outputs, status, errors)
