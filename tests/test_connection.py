"""Tests for interface class."""

from aiohttp import ClientSession, CookieJar
from aiohttp.client_exceptions import InvalidUrlClientError
from aiohttp.test_utils import TestClient, TestServer, loop_context
from unittest.mock import patch
import pytest
from typing import Any

from aioptdevices.configuration import Configuration
from aioptdevices.errors import (
    PTDevicesForbiddenError,
    PTDevicesRequestError,
    PTDevicesUnauthorizedError,
)
from aioptdevices.interface import Interface, PTDevicesResponse

# Add your token and device ID, **keep out of git**
from .mock_api import (
    API_URL,
    BAD_GATEWAY_ERROR_DEVICE_ID,
    EMPTY_ERROR_DEVICE_ID,
    FORBIDDEN_ERROR_DEVICE_ID,
    GOOD_RESP_DICT,
    NORMAL_DEVICE_ID,
    NORMAL_DEVICE_MAC,
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

            with patch(
                "aiohttp.ClientSession.request",
                side_effect=TimeoutError,
            ):
                with pytest.raises(PTDevicesRequestError):
                    await interface.get_data()

        loop.run_until_complete(test_errors())
        loop.run_until_complete(client.close())


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
