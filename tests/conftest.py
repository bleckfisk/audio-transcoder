from botocore.exceptions import ClientError
import pytest
from uuid import uuid4


@pytest.fixture
def s3_bucket():
    from service.aws_boto3 import create_s3_resource
    resource = create_s3_resource()

    bucket_name = str(uuid4())
    try:
        bucket = resource.create_bucket(Bucket=bucket_name)
    except ClientError:
        bucket = resource.Bucket(bucket_name)
        bucket.objects.all().delete()
    yield bucket
    bucket.objects.all().delete()
    bucket.delete()


@pytest.fixture
def sns_topic_arn():
    from service.aws_boto3 import create_sns_resource

    resource = create_sns_resource()
    topic_name = str(uuid4())
    response = resource.meta.client.create_topic(Name=topic_name)

    yield response["TopicArn"]
