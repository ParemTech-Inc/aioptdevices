"""Common Test Helpers used by PyTest."""

from aiohttp import web
import pytest

from .mock_api import (
    API_URL,
    BAD_GATEWAY_ERROR_DEVICE_ID,
    FORBIDDEN_ERROR_DEVICE_ID,
    NORMAL_DEVICE_ID,
    NORMAL_DEVICE_MAC,
    UNAUTHORIZED_ERROR_DEVICE_ID,
    WRONG_CONTENT_TYPE_DEVICE_ID,
    bad_gateway_response,
    content_type_invalid_response,
    forbidden_response,
    good_response,
    unauthorized_response,
)


@pytest.fixture(name="test_web_app")
def test_web_app() -> web.Application:
    """Create a test server for testing."""
    app = web.Application()
    app.router.add_get(f"{API_URL}/device/{NORMAL_DEVICE_ID}", good_response)  # type: ignore  # noqa: PGH003
    app.router.add_get(f"{API_URL}/device/{NORMAL_DEVICE_MAC}", good_response)  # type: ignore  # noqa: PGH003

    app.router.add_get(
        f"{API_URL}/device/{UNAUTHORIZED_ERROR_DEVICE_ID}", unauthorized_response
    )  # type: ignore  # noqa: PGH003
    app.router.add_get(
        f"{API_URL}/device/{FORBIDDEN_ERROR_DEVICE_ID}", forbidden_response
    )  # type: ignore  # noqa: PGH003
    app.router.add_get(
        f"{API_URL}/device/{BAD_GATEWAY_ERROR_DEVICE_ID}", bad_gateway_response
    )  # type: ignore  # noqa: PGH003
    app.router.add_get(
        f"{API_URL}/device{WRONG_CONTENT_TYPE_DEVICE_ID}", content_type_invalid_response
    )  # type: ignore  # noqa: PGH003

    return app
