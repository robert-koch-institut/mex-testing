from typing import TYPE_CHECKING

from fastapi import HTTPException

from mex.testing.settings import TestingSettings

if TYPE_CHECKING:
    from pathlib import Path


def find_test_data_file(test_data_path: str) -> Path:
    """Resolve a request path to a single asset file or raise ``HTTPException`` 404."""
    # paths starting with an underscore are reserved for internal routes (e.g. _system)
    if test_data_path.startswith("_"):
        raise HTTPException(status_code=404, detail="No files found")
    settings = TestingSettings.get()
    data_directory = (settings.http_server_test_data_directory / "").resolve()
    path_to_file_without_ext = (
        settings.http_server_test_data_directory / test_data_path
    ).resolve()
    # guard against path traversal (e.g. `../`) escaping the configured data directory
    if not path_to_file_without_ext.is_relative_to(data_directory):
        raise HTTPException(status_code=404, detail="No files found")
    found_files = list(
        path_to_file_without_ext.parent.glob(path_to_file_without_ext.name + ".*")
    )
    len_found_files = len(found_files)
    if len_found_files == 0:
        raise HTTPException(status_code=404, detail="No files found")
    if len_found_files > 1:
        raise HTTPException(status_code=404, detail="Too many files found")
    return found_files[0]
