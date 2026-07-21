from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

from mex.common.settings import BaseSettings


class SeedSettings(BaseSettings):
    """Settings definition for the SQL seeder entrypoint.

    Settings are accessed through the lazily-loaded singleton via `SeedSettings.get()`.
    """

    model_config = SettingsConfigDict(env_prefix="seed_")

    host: str = Field(
        "localhost",
        description="Host name of the target SQL Server.",
    )
    port: int = Field(
        1433,
        description="Port of the target SQL Server.",
    )
    sa_password: SecretStr = Field(
        SecretStr("password"),
        description="Password of the target SQL Server's `sa` login.",
    )
    directory: Path = Field(
        Path("seeds"),
        description="Directory holding the `*.sql` seed files to apply.",
    )
    wait_seconds: int = Field(
        120,
        description="Maximum seconds to wait for the server to accept connections.",
    )

    def dsn(self) -> str:
        """Build the ODBC connection string for the target server."""
        return (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={self.host},{self.port};"
            f"UID=sa;PWD={self.sa_password.get_secret_value()};"
            "TrustServerCertificate=yes"
        )
