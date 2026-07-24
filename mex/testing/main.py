import mimetypes
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, Response

from mex.common.cli import entrypoint
from mex.common.connector import CONNECTOR_STORE
from mex.common.logging import logger
from mex.testing.logging import UVICORN_LOGGING_CONFIG
from mex.testing.settings import TestingSettings
from mex.testing.system.main import router as system_router

startup_tasks: list[Callable[[], Any]] = [
    TestingSettings.get,
]
teardown_tasks: list[Callable[[], Any]] = [
    CONNECTOR_STORE.reset,
]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Async context manager to execute startup and teardown of the FastAPI app."""
    for task in startup_tasks:
        task()
        task_name = getattr(task, "__wrapped__", task).__name__
        logger.info(f"startup {task_name} complete")
    yield None
    for task in teardown_tasks:
        task()
        task_name = getattr(task, "__wrapped__", task).__name__
        logger.info(f"teardown {task_name} complete")


app = FastAPI(
    title="mex-testing",
    summary="Robert Koch-Institut Metadata Exchange testing service API",
    description=(
        "The MEx testing service API includes endpoints for multiple test-cases, "
        "e.g. for mocking external systems during extractor integration tests."
    ),
    contact={
        "name": "RKI MEx Team",
        "email": "mex@rki.de",
        "url": "https://github.com/robert-koch-institut/mex-testing",
    },
    strict_content_type=False,
    lifespan=lifespan,
    version="v0",
)

router = APIRouter(prefix="/v0")

# add csv manually to avoid return application/vnd.ms-excel on local windows machines
mimetypes.add_type("text/csv", ".csv")

# include explicit routes before the catch-all below so they take precedence
router.include_router(system_router)


@router.post("/datscha_web/login.php")
def post_datscha_web_login() -> RedirectResponse:
    """Login logic for datscha web."""
    return RedirectResponse("verzeichnis.php")


def _find_test_data_file(test_data_path: str) -> Path:
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


@router.api_route("/{test_data_path:path}", methods=["GET", "POST"])
def http_test_server(test_data_path: str) -> FileResponse:
    """Return http server test data defined in mex-assets."""
    found_file = _find_test_data_file(test_data_path)
    # `guess_type` (not the 3.13+ `guess_file_type`) keeps this importable on py3.11;
    # our asset filenames contain no url-special chars, so the results are equivalent
    mimetype, _ = mimetypes.guess_type(found_file)
    return FileResponse(found_file, media_type=mimetype)


@router.head("/{test_data_path:path}")
def head_http_test_server(test_data_path: str) -> Response:
    """HEAD endpoint mirroring GET availability, without a response body."""
    try:
        _find_test_data_file(test_data_path)
    except HTTPException as error:
        return Response(status_code=error.status_code)
    return Response(status_code=200)


app.include_router(router)


@entrypoint()
def main() -> None:  # pragma: no cover
    """Start the testing server process.

    Initializes and runs the FastAPI application using uvicorn server.
    Loads configuration from TestingSettings and starts the HTTP server
    on the configured host and port.
    """
    settings = TestingSettings.get()
    uvicorn.run(
        "mex.testing.main:app",
        host=settings.http_server_host,
        port=settings.http_server_port,
        root_path=settings.http_server_root_path,
        reload=settings.debug,
        log_config=UVICORN_LOGGING_CONFIG,
        headers=[("server", "mex-testing")],
    )
