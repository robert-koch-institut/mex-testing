from pathlib import Path

from fastapi import HTTPException

from mex.common.assets import FilesystemAssetsConnector
from mex.testing.settings import TestingSettings


def find_test_data_file(test_data_path: str) -> Path:
    """Resolve a request path to a single asset file or raise ``HTTPException`` 404."""
    # paths starting with an underscore are reserved for internal routes (e.g. _system)
    if test_data_path.startswith("_"):
        raise HTTPException(status_code=404, detail="No files found")
    connector = FilesystemAssetsConnector.get()
    settings = TestingSettings.get()
    test_data_files = connector.glob(
        f"{settings.http_server_test_data_directory}/{test_data_path}", "*.*"
    )
    len_found_files = len(test_data_files)
    if len_found_files == 0:
        raise HTTPException(status_code=404, detail="No files found")
    if len_found_files > 1:
        raise HTTPException(status_code=404, detail="Too many files found")
    return Path(test_data_files[0])
