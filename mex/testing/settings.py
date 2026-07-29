from pydantic import Field

from mex.common.settings import BaseSettings
from mex.common.types import AssetsPath


class TestingSettings(BaseSettings):
    """Settings definition for the testing service."""

    http_server_host: str = Field(
        "localhost",
        min_length=1,
        max_length=250,
        description="Host that the http server will run on.",
        validation_alias="MEX_TESTING_HTTP_SERVER_HOST",
    )
    http_server_port: int = Field(
        8088,
        gt=0,
        lt=65536,
        description="Port that the http server should listen on.",
        validation_alias="MEX_TESTING_HTTP_SERVER_PORT",
    )
    http_server_root_path: str = Field(
        "",
        description="Root path that the http server should run under.",
        validation_alias="MEX_TESTING_HTTP_SERVER_ROOT_PATH",
    )
    http_server_test_data_directory: AssetsPath = Field(
        AssetsPath("."),
        description="Directory that the http server should return test data from.",
        validation_alias="MEX_TESTING_HTTP_SERVER_DATA_DIRECTORY",
    )
