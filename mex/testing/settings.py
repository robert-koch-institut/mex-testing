from pathlib import Path

from pydantic import Field, SecretStr

from mex.common.settings import BaseSettings
from mex.common.types import AssetsPath


class TestingSettings(BaseSettings):
    """Settings definition for the testing service."""

    sql_seed_host: str = Field(
        "localhost",
        description="Host name of the target SQL Server.",
        validation_alias="MEX_TESTING_SQL_SEED_HOST",
    )
    sql_seed_port: int = Field(
        1433,
        description="Port of the target SQL Server.",
        validation_alias="MEX_TESTING_SQL_SEED_PORT",
    )
    sql_seed_sa_password: SecretStr = Field(
        SecretStr("MEx_testing1234"),
        description="Password of the target SQL Server's `sa` login.",
        validation_alias="MEX_TESTING_SQL_SEED_SA_PASSWORD",
    )
    sql_seed_directory: Path = Field(
        Path("seeds"),
        description="Directory holding the `*.sql` seed files to apply.",
        validation_alias="MEX_TESTING_SQL_SEED_DIRECTORY",
    )
    sql_seed_wait_seconds: int = Field(
        120,
        description="Maximum seconds to wait for the server to accept connections.",
        validation_alias="MEX_TESTING_SQL_SEED_WAIT_SECONDS",
    )

    def sql_seed_dsn(self) -> str:
        """Build the ODBC connection string for the target server."""
        return (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={self.sql_seed_host},{self.sql_seed_port};"
            f"UID=sa;PWD={self.sql_seed_sa_password.get_secret_value()};"
            "TrustServerCertificate=yes"
        )

    http_server_host: str = Field(
        "localhost",
        min_length=1,
        max_length=250,
        description="Host that the http server will run on.",
        validation_alias="MEX_TESTING_HTTP_SERVER_HOST",
    )
    http_server_port: int = Field(
        8050,
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
