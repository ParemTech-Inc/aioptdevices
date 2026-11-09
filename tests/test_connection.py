"""Tests for interface class."""

import logging
from typing import Any
from unittest.mock import patch

from aiohttp import ClientSession, CookieJar
from aiohttp.test_utils import TestClient, TestServer, loop_context
import pytest

from aioptdevices.configuration import Configuration
from aioptdevices.errors import (
    PTDevicesForbiddenError,
    PTDevicesParseError,
    PTDevicesRequestError,
    PTDevicesUnauthorizedError,
)
from aioptdevices.interface import (
    Interface,
    PTDevicesResponse,
    _format_data,
    _ParseIssueLog,
)

# Add your token and device ID, **keep out of git**
from .mock_api import (
    ALL_FAIL_PARSE_DEVICE_ID,
    API_URL,
    BAD_GATEWAY_ERROR_DEVICE_ID,
    EMPTY_ERROR_DEVICE_ID,
    FORBIDDEN_ERROR_DEVICE_ID,
    GOOD_RESP_DICT,
    GOOD_RESP_DICT_UK_IMP,
    GOOD_RESP_DICT_US_IMP,
    INVALID_JSON_DEVICE_ID,
    MISSING_DATA_DEVICE_ID,
    NORMAL_DEVICE_ID,
    NORMAL_DEVICE_ID_UK,
    NORMAL_DEVICE_ID_US,
    NORMAL_DEVICE_MAC,
    PARTIAL_PARSE_DEVICE_ID,
    REDIRECT_ERROR_DEVICE_ID,
    TOKEN,
    UNAUTHORIZED_ERROR_DEVICE_ID,
    WRONG_CONTENT_TYPE_DEVICE_ID,
)
from .secret import DEVICE_ID as secret_DEVICE_ID, TOKEN as secret_TOKEN

# Query Paramaters


def test_interface(test_web_app):
    """Test the basic interface connection."""
    with loop_context() as loop:
        # Setup the test server
        server = TestServer(test_web_app)
        client = TestClient(server, loop=loop)
        loop.run_until_complete(client.start_server())

        normal_config: Configuration = Configuration(
            auth_token=TOKEN,
            device_id=NORMAL_DEVICE_ID,
            url=str(client.make_url(API_URL)),
            session=client.session,
        )
        interface: Interface = Interface(normal_config)

        async def test_get_data():
            resp: PTDevicesResponse = await interface.get_data()
            assert resp.get("body") == GOOD_RESP_DICT

        loop.run_until_complete(test_get_data())
        loop.run_until_complete(client.close())


def test_mac_id(test_web_app):
    """Test the basic interface connection."""
    with loop_context() as loop:
        # Setup the test server
        server = TestServer(test_web_app)
        client = TestClient(server, loop=loop)
        loop.run_until_complete(client.start_server())

        normal_config: Configuration = Configuration(
            auth_token=TOKEN,
            device_id=NORMAL_DEVICE_MAC,
            url=str(client.make_url(API_URL)),
            session=client.session,
        )
        interface: Interface = Interface(normal_config)

        async def test_get_data():
            resp: PTDevicesResponse = await interface.get_data()
            assert resp.get("body") == GOOD_RESP_DICT

        loop.run_until_complete(test_get_data())
        loop.run_until_complete(client.close())


def test_unit_conversion(test_web_app):
    """Test the automatic unit conversion."""
    with loop_context() as loop:
        # Setup the test server
        server = TestServer(test_web_app)
        client = TestClient(server, loop=loop)
        loop.run_until_complete(client.start_server())

        # Test US Units
        normal_config: Configuration = Configuration(
            auth_token=TOKEN,
            device_id=NORMAL_DEVICE_ID_US,
            url=str(client.make_url(API_URL)),
            session=client.session,
        )
        interface: Interface = Interface(normal_config)

        async def test_get_data_us():
            resp: PTDevicesResponse = await interface.get_data()
            assert resp.get("body") == GOOD_RESP_DICT_US_IMP

        loop.run_until_complete(test_get_data_us())

        # Test UK Units
        normal_config: Configuration = Configuration(
            auth_token=TOKEN,
            device_id=NORMAL_DEVICE_ID_UK,
            url=str(client.make_url(API_URL)),
            session=client.session,
        )
        interface: Interface = Interface(normal_config)

        async def test_get_data_uk():
            resp: PTDevicesResponse = await interface.get_data()
            assert resp.get("body") == GOOD_RESP_DICT_UK_IMP

        loop.run_until_complete(test_get_data_uk())
        loop.run_until_complete(client.close())


def test_resp_error_handling(test_web_app):
    """Test the interface with different response statuses."""
    with loop_context() as loop:
        # Setup the test server
        server = TestServer(test_web_app)
        client = TestClient(server, loop=loop)

        loop.run_until_complete(client.start_server())

        def make_interface(device_id: str) -> Interface:
            return Interface(
                Configuration(
                    auth_token=TOKEN,
                    device_id=device_id,
                    url=str(client.make_url(API_URL)),
                    session=client.session,
                )
            )

        async def test_errors():
            # UNAUTHORIZED (401) Handling
            interface: Interface = make_interface(UNAUTHORIZED_ERROR_DEVICE_ID)

            with pytest.raises(PTDevicesUnauthorizedError):  # Test UNAUTHORIZED (401)
                await interface.get_data()

            # FORBIDDEN (403) Handling
            interface: Interface = make_interface(FORBIDDEN_ERROR_DEVICE_ID)

            with pytest.raises(PTDevicesForbiddenError):  # Test UNAUTHORIZED (401)
                await interface.get_data()

            # FORBIDDEN (302) Handling
            interface: Interface = make_interface(REDIRECT_ERROR_DEVICE_ID)

            with pytest.raises(PTDevicesUnauthorizedError):  # Test UNAUTHORIZED (401)
                await interface.get_data()

            # PTDevicesRequestError (403) Handling
            interface: Interface = make_interface(BAD_GATEWAY_ERROR_DEVICE_ID)

            with pytest.raises(PTDevicesRequestError):  # Test UNAUTHORIZED (401)
                await interface.get_data()

            # Wrong content type Handling
            interface: Interface = make_interface(WRONG_CONTENT_TYPE_DEVICE_ID)

            with pytest.raises(PTDevicesRequestError):  # Test UNAUTHORIZED (401)
                await interface.get_data()

            # FORBIDDEN (302) Handling
            interface: Interface = make_interface(EMPTY_ERROR_DEVICE_ID)

            with pytest.raises(PTDevicesRequestError):  # Test UNAUTHORIZED (401)
                await interface.get_data()

            with (
                patch(
                    "aiohttp.ClientSession.request",
                    side_effect=TimeoutError,
                ),
                pytest.raises(PTDevicesRequestError),
            ):
                await interface.get_data()

        loop.run_until_complete(test_errors())
        loop.run_until_complete(client.close())


def test_partial_parse(test_web_app):
    """Test that one device failing to parse does not fail the whole response."""
    with loop_context() as loop:
        server = TestServer(test_web_app)
        client = TestClient(server, loop=loop)
        loop.run_until_complete(client.start_server())

        interface: Interface = Interface(
            Configuration(
                auth_token=TOKEN,
                device_id=PARTIAL_PARSE_DEVICE_ID,
                url=str(client.make_url(API_URL)),
                session=client.session,
            )
        )

        async def test_get_data():
            resp: PTDevicesResponse = await interface.get_data()

            # The device missing user_id is reported as failed and left out of body,
            # the entry without a device_id is skipped entirely
            assert set(resp["body"]) == {"AAAAAAAAAAAA", "BBBBBBBBBBBB"}
            assert resp["failed"] == {"CCCCCCCCCCCC"}

            # Versions are passed through as received, numbers become strings
            good = resp["body"]["AAAAAAAAAAAA"]
            assert good["version"] == "v1.40b"
            assert good["status"] == "working"
            assert good["wifi_signal"] == 80
            assert good["depth_level"] == 0.508

            # Fields that fail to parse become None, the rest of the device parses
            bad = resp["body"]["BBBBBBBBBBBB"]
            assert bad["version"] == "208"
            assert bad["status"] == "unknown"
            assert bad["wifi_signal"] is None
            assert bad["percent_level"] is None
            assert bad["tx_signal"] == -50.0
            assert bad["depth_level"] is None
            assert "inch_level" not in bad

        loop.run_until_complete(test_get_data())
        loop.run_until_complete(client.close())


def test_all_devices_fail_to_parse(test_web_app):
    """Test that a response where every device fails to parse raises."""
    with loop_context() as loop:
        server = TestServer(test_web_app)
        client = TestClient(server, loop=loop)
        loop.run_until_complete(client.start_server())

        interface: Interface = Interface(
            Configuration(
                auth_token=TOKEN,
                device_id=ALL_FAIL_PARSE_DEVICE_ID,
                url=str(client.make_url(API_URL)),
                session=client.session,
            )
        )

        async def test_get_data():
            with pytest.raises(PTDevicesParseError):
                await interface.get_data()

        loop.run_until_complete(test_get_data())
        loop.run_until_complete(client.close())


def test_malformed_response(test_web_app):
    """Test that a body that is not JSON or has no data key raises."""
    with loop_context() as loop:
        server = TestServer(test_web_app)
        client = TestClient(server, loop=loop)
        loop.run_until_complete(client.start_server())

        def make_interface(device_id: str) -> Interface:
            return Interface(
                Configuration(
                    auth_token=TOKEN,
                    device_id=device_id,
                    url=str(client.make_url(API_URL)),
                    session=client.session,
                )
            )

        async def test_errors():
            with pytest.raises(PTDevicesParseError):
                await make_interface(INVALID_JSON_DEVICE_ID).get_data()

            with pytest.raises(PTDevicesParseError):
                await make_interface(MISSING_DATA_DEVICE_ID).get_data()

        loop.run_until_complete(test_errors())
        loop.run_until_complete(client.close())


def _device(**overrides: Any) -> dict[str, Any]:
    """Return a minimal raw device for _format_data."""
    return {
        "id": 1,
        "device_id": "AAAAAAAAAAAA",
        "user_id": 1234,
        "device_type": "level",
        "title": "Test",
        "version": "208",
        "status_number": 2,
        "wifi_signal": "80%",
        **overrides,
    }


def _count(caplog: pytest.LogCaptureFixture, level: int, text: str) -> int:
    """Count log records at a level whose message contains text."""
    return sum(
        1 for r in caplog.records if r.levelno == level and text in r.getMessage()
    )


def test_parse_issues_log_once(caplog: pytest.LogCaptureFixture):
    """Test a repeated parse issue warns once, then logs when it is resolved."""
    log = _ParseIssueLog()
    caplog.set_level(logging.DEBUG, logger="aioptdevices")

    # The same bad field and failed device over two polls warn once each
    for _ in range(2):
        _format_data([_device(wifi_signal="n/a"), {"device_id": "BBBBBBBBBBBB"}], log)
    assert _count(caplog, logging.WARNING, "could not parse wifi_signal") == 1
    assert _count(caplog, logging.DEBUG, "could not parse wifi_signal") == 1
    assert _count(caplog, logging.WARNING, "BBBBBBBBBBBB: failed to parse") == 1
    assert _count(caplog, logging.DEBUG, "BBBBBBBBBBBB: failed to parse") == 1
    failures = [r for r in caplog.records if "BBBBBBBBBBBB: failed" in r.getMessage()]
    assert [bool(r.exc_info) for r in failures] == [True, False]

    # Both parse again, so each logs a single resolved message
    caplog.clear()
    _format_data([_device(), _device(device_id="BBBBBBBBBBBB")], log)
    assert _count(caplog, logging.INFO, "AAAAAAAAAAAA: wifi_signal parsed") == 1
    assert _count(caplog, logging.INFO, "BBBBBBBBBBBB: device parsed") == 1
    assert _count(caplog, logging.WARNING, "") == 0

    # A new failure after resolving warns again
    caplog.clear()
    _format_data([_device(wifi_signal="n/a")], log)
    assert _count(caplog, logging.WARNING, "could not parse wifi_signal") == 1


def test_parse_issue_for_removed_device_is_dropped(caplog: pytest.LogCaptureFixture):
    """Test issues for a device that leaves the response are dropped silently."""
    log = _ParseIssueLog()
    caplog.set_level(logging.DEBUG, logger="aioptdevices")

    _format_data([_device(), _device(device_id="BBBBBBBBBBBB", wifi_signal="n/a")], log)
    caplog.clear()
    _format_data([_device()], log)

    assert not [r for r in caplog.records if r.levelno >= logging.INFO]


def test_real_server():
    """Test the interface with the real server."""
    with loop_context() as loop:
        # Setup the test server

        async def test_real_server():
            session: ClientSession = ClientSession(cookie_jar=CookieJar(unsafe=True))
            interface: Interface = Interface(
                Configuration(
                    auth_token=secret_TOKEN,
                    device_id=secret_DEVICE_ID,
                    url="https://api.ptdevices.com/token/v1",
                    session=session,
                )
            )
            resp: PTDevicesResponse = await interface.get_data()
            data: dict[str, dict[str, Any]] = resp.get("body", {})
            assert data
            assert "device_id" in list(data.values())[0]
            await session.close()

        loop.run_until_complete(test_real_server())


def test_real_server_multi():
    """Test the interface with the real server."""
    with loop_context() as loop:
        # Setup the test server

        async def test_real_server():
            session: ClientSession = ClientSession(cookie_jar=CookieJar(unsafe=True))
            interface: Interface = Interface(
                Configuration(
                    auth_token=secret_TOKEN,
                    device_id="*",
                    url="https://api.ptdevices.com/token/v1",
                    session=session,
                )
            )
            resp: PTDevicesResponse = await interface.get_data()
            data: dict[str, dict[str, Any]] = resp.get("body", {})
            assert data
            assert "device_id" in list(data.values())[0]
            await session.close()

        loop.run_until_complete(test_real_server())
