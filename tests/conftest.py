import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mex.common.logging import logger
from mex.testing.main import app
from mex.testing.settings import TestingSettings

TEST_DATA_PATH = Path(__file__).parent / "test_data"

pytest_plugins = ("mex.common.testing.plugin",)


@pytest.fixture
def log_level(request: pytest.FixtureRequest) -> int:
    """Returns a sensible log-level for the current pytest verbosity.

    This can be controlled by adding more "v"s to `pytest -v`.
    """
    levels_by_verbosity = {
        0: logging.ERROR,  # always shown
        1: logging.WARNING,  # -v
        2: logging.INFO,  # -vv
    }
    return levels_by_verbosity.get(
        request.config.option.verbose,
        logging.DEBUG,  # `-vvv` and above
    )


@pytest.fixture(autouse=True)
def settings(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    log_level: int,
) -> TestingSettings:
    """Load the settings for this pytest session."""
    monkeypatch.setenv(
        "MEX_TESTING_HTTP_SERVER_DATA_DIRECTORY",
        str(TEST_DATA_PATH),
    )
    # temporarily reduce log-level because the settings emit their configuration
    # on every instantiation or value-change. this would flood the test logs with noise,
    # especially because this fixture is used by *every* test.
    with caplog.at_level(log_level, logger=logger.name):
        return TestingSettings.get()


@pytest.fixture
def client() -> TestClient:
    """Return a fastAPI test client initialized with our app."""
    with TestClient(app, raise_server_exceptions=False) as test_client:
        return test_client
