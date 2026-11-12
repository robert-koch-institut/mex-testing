from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from fastapi import FastAPI, Request, Response

SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Frame-Options": "DENY",
}
# the api only serves mock data, so nothing may be loaded or framed
API_CSP = "default-src 'none'; frame-ancestors 'none'"
# the swagger ui loads its js and css from jsdelivr and runs one inline script
DOCS_CSP = (
    "default-src 'none'; "
    "script-src https://cdn.jsdelivr.net 'unsafe-inline'; "
    "style-src https://cdn.jsdelivr.net; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'"
)
DOCS_PATHS = ("/docs", "/docs/oauth2-redirect")


def add_security_headers(app: FastAPI) -> None:
    """Set security headers on every http response of the given app."""

    @app.middleware("http")
    async def set_security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers.update(SECURITY_HEADERS)
        response.headers["Content-Security-Policy"] = (
            DOCS_CSP if request.url.path.endswith(DOCS_PATHS) else API_CSP
        )
        response.headers.setdefault("Cache-Control", "no-store")
        return response
