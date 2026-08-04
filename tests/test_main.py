from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import pytest

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

TEST_DATA_PATH = Path(__file__).parent / "test_data"


@dataclass
class SuccessResponseExpectation:
    mimetype: str = ""
    file_content: bytes = b""


@dataclass
class ErrorResponseExpectation:
    detail_message: str = ""


@dataclass
class HttpTestServerExpectedResponse:
    status_code: int
    expectation: SuccessResponseExpectation | ErrorResponseExpectation


def _read_file_content(file_path: str) -> bytes:
    with (TEST_DATA_PATH / file_path).open("rb") as f:
        return f.read()


successful_json = HttpTestServerExpectedResponse(
    status_code=200,
    expectation=SuccessResponseExpectation(
        "application/json", file_content=_read_file_content("extractor/test_data.json")
    ),
)
successful_csv = HttpTestServerExpectedResponse(
    status_code=200,
    expectation=SuccessResponseExpectation(
        "text/csv; charset=utf-8",
        file_content=_read_file_content("extractor/test_table.csv"),
    ),
)
not_existing_file = HttpTestServerExpectedResponse(
    status_code=404, expectation=ErrorResponseExpectation("No files found")
)
too_many_file = HttpTestServerExpectedResponse(
    status_code=404, expectation=ErrorResponseExpectation("Too many files found")
)


@pytest.mark.parametrize(
    ("method", "path", "expected_response"),
    [
        pytest.param(
            "GET", "extractor/test_data", successful_json, id="successful_get_json"
        ),
        pytest.param(
            "POST", "extractor/test_data", successful_json, id="successful_post_json"
        ),
        pytest.param(
            "GET", "extractor/test_table", successful_csv, id="successful_get_csv"
        ),
        pytest.param(
            "POST", "extractor/test_table", successful_csv, id="successful_post_csv"
        ),
        pytest.param(
            "GET",
            "extractor/not_existing",
            not_existing_file,
            id="error_get_file_not_found",
        ),
        pytest.param(
            "POST",
            "extractor/not_existing",
            not_existing_file,
            id="error_post_file_not_found",
        ),
        pytest.param(
            "GET",
            "extractor/too_many_files",
            too_many_file,
            id="error_get_too_many_files",
        ),
        pytest.param(
            "POST",
            "extractor/too_many_files",
            too_many_file,
            id="error_post_too_many_files",
        ),
    ],
)
def test_http_test_server(
    method: Literal["GET", "POST"],
    path: str,
    expected_response: HttpTestServerExpectedResponse,
    client: TestClient,
) -> None:
    url = f"/v0/{path}"
    response = client.request(url=url, method=method)
    assert response.status_code == expected_response.status_code
    if isinstance(expected_response.expectation, SuccessResponseExpectation):
        assert (
            response.headers["content-type"] == expected_response.expectation.mimetype
        )
        assert response.content == expected_response.expectation.file_content
    elif isinstance(expected_response.expectation, ErrorResponseExpectation):
        assert response.json() == {
            "detail": expected_response.expectation.detail_message
        }


def test_head_http_test_server(client: TestClient) -> None:
    response = client.head("/v0/extractor/test_data")
    assert response.status_code == 200


def test_head_missing_file_returns_404(client: TestClient) -> None:
    # HEAD mirrors GET availability: 404 when GET would 404
    assert client.head("/v0/extractor/not_existing").status_code == 404
    assert client.head("/v0/extractor/too_many_files").status_code == 404


def test_path_traversal_is_blocked(client: TestClient) -> None:
    # `..%2f..%2fpyproject` reaches the handler as `../../pyproject`, which would
    # otherwise resolve to and serve the repo's `pyproject.toml`
    for method in ("GET", "HEAD"):
        response = client.request(method, "/v0/..%2f..%2fpyproject")
        assert response.status_code == 404
        assert b"[project]" not in response.content


def test_post_datscha_web_login(client: TestClient) -> None:
    response = client.post("/v0/datscha_web/login.php", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "verzeichnis.php"


def test_underscore_paths_are_not_served(client: TestClient) -> None:
    assert client.get("/v0/_secret").status_code == 404
    assert client.head("/v0/_secret").status_code == 404
