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
