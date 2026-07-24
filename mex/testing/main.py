import mimetypes
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
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


@router.api_route("/{test_data_path:path}", methods=["GET", "POST"])
def http_test_server(test_data_path: str) -> FileResponse:
    """Return http server test data defined in mex-assets."""
    # paths starting with an underscore are reserved for internal routes (e.g. _system)
    if test_data_path.startswith("_"):
        msg = "No files found"
        raise HTTPException(status_code=404, detail=msg)
    settings = TestingSettings.get()
    path_to_file_without_ext = settings.http_server_test_data_directory / test_data_path
    found_files = list(
        path_to_file_without_ext.parent.glob(path_to_file_without_ext.name + ".*")
    )
    len_found_files = len(found_files)
    if len_found_files == 0:
        msg = "No files found"
        raise HTTPException(status_code=404, detail=msg)
    if len_found_files > 1:
        msg = "Too many files found"
        raise HTTPException(status_code=404, detail=msg)

    found_file = found_files[0]
    mimetype, _ = mimetypes.guess_file_type(found_file)

    return FileResponse(found_file, media_type=mimetype)


@router.head("/{test_data_path:path}")
def head_http_test_server(test_data_path: str) -> Response:
    """HEAD endpoint for checking availability."""
    # paths starting with an underscore are reserved for internal routes (e.g. _system)
    if test_data_path.startswith("_"):
        return Response(status_code=404)
    return Response(status_code=200)


app.include_router(router)


@entrypoint(TestingSettings)
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
