from glob import escape
from typing import TYPE_CHECKING

from fastapi import HTTPException

from mex.testing.settings import TestingSettings

if TYPE_CHECKING:
    from pathlib import Path


def resolve_test_data_path(test_data_path: str) -> Path:
    """Resolve a request path within the test data directory or raise 404."""
    # paths starting with an underscore are reserved for internal routes (e.g. _system)
    if test_data_path.startswith("_"):
        raise HTTPException(status_code=404, detail="No files found")
    settings = TestingSettings.get()
    data_directory = (settings.http_server_test_data_directory / "").resolve()
    resolved_path = (
        settings.http_server_test_data_directory / test_data_path
    ).resolve()
    # guard against path traversal (e.g. `../`) escaping the configured data directory
    if not resolved_path.is_relative_to(data_directory):
        raise HTTPException(status_code=404, detail="No files found")
    return resolved_path


def find_test_data_file(test_data_path: str, query: str = "") -> Path:
    """Resolve a request path to a single asset file or raise ``HTTPException`` 404.

    When a query string is given, a file named `{name}@{query}.{ext}` is preferred
    over the plain `{name}.{ext}`. Like `wget --restrict-file-names=windows`, we use
    `@` in place of `?`, because the latter is not allowed in windows file names.
    The query is matched exactly as it was sent, i.e. still percent-encoded.
    """
    path_without_ext = resolve_test_data_path(test_data_path)
    found_files: list[Path] = []
    # a query containing path separators could escape the parent directory
    if query and not {"/", "\\"} & set(query):
        found_files = list(
            path_without_ext.parent.glob(
                escape(f"{path_without_ext.name}@{query}.") + "*"
            )
        )
    if not found_files:
        found_files = list(
            path_without_ext.parent.glob(escape(f"{path_without_ext.name}.") + "*")
        )
    len_found_files = len(found_files)
    if len_found_files == 0:
        raise HTTPException(status_code=404, detail="No files found")
    if len_found_files > 1:
        raise HTTPException(status_code=404, detail="Too many files found")
    return found_files[0]


def is_test_data_directory(test_data_path: str) -> bool:
    """Return whether a request path points to a directory of test data."""
    try:
        return resolve_test_data_path(test_data_path).is_dir()
    except HTTPException:
        return False
