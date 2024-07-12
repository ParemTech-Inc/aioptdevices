"""Python Library for communicating with PTDevices"""

import logging
from typing import Any, TypedDict

from aiohttp import client_exceptions
from http import HTTPStatus

import orjson

from aioptdevices.errors import (
    PTDevicesForbiddenError,
    PTDevicesRequestError,
    PTDevicesUnauthorizedError,
)

from .configuration import Configuration

LOGGER = logging.getLogger(__name__)


class PTDevicesResponse(TypedDict, total=False):
    """Typed Response from PTDevices"""

    body: dict[str, Any]
    code: int


class Interface:
    """Interface for PTDevices"""

    def __init__(self, config: Configuration) -> None:
        """Connection Session Setup"""
        self.config = config

    async def get_data(self) -> PTDevicesResponse:
        """Fetch device data from PTDevices server and format it"""
        # Request url: https://api.ptdevices.com/token/v1/device/{deviceId}?api_token={given_token}
        # Where
        #   {deviceId} is the numeric internal device id, found in the url https://www.ptdevices.com/device/level/{deviceId}
        #   {given_token} is the access token you were given

        url = (
            f"{self.config.url}{self.config.deviceId}?api_token={self.config.authToken}"
        )

        LOGGER.debug(
            f"Sending request to {self.config.url} for data from device #{self.config.deviceId}"
        )

        try:
            async with self.config.session.request(
                "get",
                url,
            ) as results:
                LOGGER.debug(
                    f"{results.status} Received from {self.config.url}, {results}"
                )

                # Check return code
                if results.status == HTTPStatus.UNAUTHORIZED:
                    raise PTDevicesUnauthorizedError(
                        f"Request to {url} failed, the token provided is not valid"
                    )

                if results.status == HTTPStatus.FORBIDDEN:
                    raise PTDevicesForbiddenError(
                        f"Request to {url} failed, the token provided is not valid for device {self.config.deviceId}"
                    )

                if results.status != HTTPStatus.OK:
                    raise PTDevicesRequestError(
                        f"Request to {url} failed, got unexpected response from server ({results.status})"
                    )

                # Check content type
                if (
                    results.content_type != "application/json"
                    or results.content_length == 0
                ):
                    raise PTDevicesRequestError(
                        f"Failed to get device data, returned content is invalid. Type: {results.content_type}, content Length: {results.content_length}, content: {results.content}"
                    )

                raw_json = await results.read()

                body = orjson.loads(raw_json)

                return PTDevicesResponse(
                    code=results.status,
                    body=body["data"],
                )

        except client_exceptions.ClientError as error:
            raise PTDevicesRequestError(f"Request to {url} failed: {error}")


# http://api.ptdevices.com/token/v1/device/{deviceId}?api_token={given_token}
