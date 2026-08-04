import pytest
from fastapi import HTTPException

from mex.testing.helpers import find_test_data_file


def test_find_test_data_file_returns_single_match() -> None:
    found_file = find_test_data_file("extractor/test_data")
    assert found_file.name == "test_data.json"


def test_find_test_data_file_raises_when_not_found() -> None:
    with pytest.raises(HTTPException) as error:
        find_test_data_file("extractor/not_existing")
    assert error.value.status_code == 404
    assert error.value.detail == "No files found"


def test_find_test_data_file_raises_when_too_many_found() -> None:
    with pytest.raises(HTTPException) as error:
        find_test_data_file("extractor/too_many_files")
    assert error.value.status_code == 404
    assert error.value.detail == "Too many files found"


def test_find_test_data_file_rejects_underscore_paths() -> None:
    with pytest.raises(HTTPException) as error:
        find_test_data_file("_secret")
    assert error.value.status_code == 404
    assert error.value.detail == "No files found"


def test_find_test_data_file_blocks_path_traversal() -> None:
    with pytest.raises(HTTPException) as error:
        find_test_data_file("../../pyproject")
    assert error.value.status_code == 404
    assert error.value.detail == "No files found"
