from typing import TYPE_CHECKING

import pytest
from starlette import status

from mex.testing.middleware import API_CSP, DOCS_CSP, SECURITY_HEADERS

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    ("path", "expected_csp"),
    [("/v0/_system/check", API_CSP), ("/docs", DOCS_CSP)],
    ids=["api", "docs"],
)
def test_security_headers(client: TestClient, path: str, expected_csp: str) -> None:
    response = client.get(path)

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.headers["Content-Security-Policy"] == expected_csp
    assert response.headers["Cache-Control"] == "no-store"
    for name, value in SECURITY_HEADERS.items():
        assert response.headers[name] == value


def test_redoc_is_disabled(client: TestClient) -> None:
    response = client.get("/redoc")

    assert response.status_code == status.HTTP_404_NOT_FOUND
