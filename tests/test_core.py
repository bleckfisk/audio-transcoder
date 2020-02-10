import io
import pytest
import json
from service.core import upload, download, callback, process_message
from uuid import uuid4
from service.aws_boto3 import create_s3_resource, create_sqs_resource
from botocore.exceptions import ClientError
from unittest import mock


def test_download(s3_bucket):

    """
    Tests proves that subject returned from download contains the
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


@mock.patch('service.loggers.AWS_Logger')
def test_download_key_not_exists(mock_AWS_Logger, s3_bucket):
    """
    Test for exception handeling.
    Will pass if the exception is raised, and is raised because of
    key not found in download function
    """

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
        assert mock_AWS_Logger.call_count == 1


@mock.patch('service.loggers.AWS_Logger')
def test_download_bucket_not_exists(mock_AWS_Logger, s3_bucket):
    """
    Test for exception handeling.
    Will pass if exception is raised, and is raised because
    the bucket does not exist.
    """

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
        assert mock_AWS_Logger.call_count == 1


def test_upload(s3_bucket):
    """
    Test proves that file created here and sent to
    upload is uploaded accordingly.
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


@mock.patch('service.loggers.AWS_Logger')
def test_upload_bucket_not_exists(mock_AWS_Logger, s3_bucket):
    """
    Test for exception handeling.
    Will pass if exception is raised, and is raised because
    the bucket does not exist.
    """

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
        assert mock_AWS_Logger.call_count == 1


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
    Test proves that callback is not throwing exceptions
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


@mock.patch("service.core.callback")
@mock.patch("service.core.upload")
@mock.patch("service.transcoder.transcode", return_value=io.BytesIO)
@mock.patch("service.core.download", return_value=io.BytesIO)
@mock.patch("service.validators.validate_message")
def test_process_message(
    mock_validate_message, mock_download, mock_transcode,
        mock_upload, mock_callback, sqs_queue):

    """
    Test for process_message many different calls to other functions.
    The dependant functions are mocked with patch so that
    process_message can be tested in isolation without actually
    calling the dependant functions.
    """

    resource = create_sqs_resource()

    messages = resource.meta.client.receive_message(
        QueueUrl=sqs_queue.get("QueueUrl"),
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0
    )

    loaded_message_body = json.loads(messages['Messages'][0]['Body'])

    process_message(loaded_message_body)

    assert mock_validate_message.called_once_with(loaded_message_body)

    assert mock_download.called_with(
        create_s3_resource(),
        loaded_message_body["input"]
        )

    for output in loaded_message_body:

        assert mock_transcode.called_with(
            io.BytesIO(),
            loaded_message_body[output]
            )

        assert mock_upload.called_with(
            create_s3_resource(),
            io.BytesIO(),
            loaded_message_body[output]
            )


@mock.patch("service.core.callback")
@mock.patch("service.core.upload")
@mock.patch("service.transcoder.transcode", return_value=io.BytesIO)
@mock.patch("service.core.download", return_value=io.BytesIO)
@mock.patch("service.validators.validate_message")
def test_process_message_bad_message_keys(
    mock_validate_message, mock_download, mock_transcode,
        mock_upload, mock_callback, sqs_queue_bad_message_keys):

    """
    This test proves that when input and output keys are bad
    we don't try to process them, instead we handle the exception and
    calls callback() accordingly.
    """

    resource = create_sqs_resource()
    sqs_queue = sqs_queue_bad_message_keys

    messages = resource.meta.client.receive_message(
        QueueUrl=sqs_queue.get("QueueUrl"),
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0
    )

    loaded_message_body = json.loads(messages['Messages'][0]['Body'])

    with pytest.raises(Exception):
        process_message(loaded_message_body)

        assert mock_validate_message.called_once_with(loaded_message_body)

        assert mock_download.call_count == 0
        assert mock_transcode.call_count == 0
        assert mock_upload.call_count == 0
        assert mock_callback.call_count == 1
