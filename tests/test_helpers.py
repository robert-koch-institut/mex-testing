import pytest
from fastapi import HTTPException

from mex.testing.helpers import find_test_data_file, is_test_data_directory


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


def test_find_test_data_file_prefers_query_specific_file() -> None:
    found_file = find_test_data_file("extractor/paged", "page=2")
    assert found_file.name == "paged@page=2.json"


def test_find_test_data_file_falls_back_to_file_without_query() -> None:
    found_file = find_test_data_file("extractor/paged", "page=3")
    assert found_file.name == "paged.json"


def test_find_test_data_file_ignores_queries_with_path_separators() -> None:
    found_file = find_test_data_file("extractor/paged", "page=2/../../x")
    assert found_file.name == "paged.json"


def test_is_test_data_directory() -> None:
    assert is_test_data_directory("extractor")
    assert not is_test_data_directory("extractor/test_data")
    assert not is_test_data_directory("not_existing")
    assert not is_test_data_directory("_secret")
