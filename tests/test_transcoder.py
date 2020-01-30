import pytest
import io
from service.transcoder import transcode
from pydub.audio_segment import CouldntDecodeError


def test_transcode_unsupported_data(unsupported_transcode_data):
    handles = unsupported_transcode_data["handles"]
    outputs = unsupported_transcode_data["outputs"]

    with pytest.raises(IndexError):
        file = io.BytesIO(handles[0].read())
        for output in outputs:
            transcode(file, output)

    with pytest.raises(CouldntDecodeError):
        file = io.BytesIO(handles[1].read())
        for output in outputs:
            transcode(file, output)


def test_transcode_supported_data(supported_transcode_data):
    file = supported_transcode_data["handles"][0]
    output = supported_transcode_data["outputs"]
    transcode(file, output)
