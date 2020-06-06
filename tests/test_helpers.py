import os
import pytest
from service.exceptions import MediaInfoIsEmptyError
from service.helpers import get_format

def test_get_format_raises_exception(list_of_supported_files):
    file_path = f"{os.getcwd()}/tests/test_samples/supported/non_existent_file_name"

    with pytest.raises(MediaInfoIsEmptyError):
        assert get_format(file_path)

def test_get_format(list_of_supported_files):
    file_name = list_of_supported_files[0]
    file_path = f"{os.getcwd()}/tests/test_samples/supported/{file_name}"
    assert get_format(file_path)
