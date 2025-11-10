"""Python Library for communicating with PTDevices."""

from http import HTTPStatus
import logging
from typing import Any, TypedDict

import orjson

from aioptdevices.errors import (
    PTDevicesForbiddenError,
    PTDevicesRequestError,
    PTDevicesUnauthorizedError,
)

from .configuration import Configuration

LOGGER = logging.getLogger(__name__)


class PTDevicesResponse(TypedDict, total=False):
    """Typed Response from PTDevices."""

    body: dict[str, Any]
    code: int


class Interface:
    """Interface for PTDevices."""

    def __init__(self, config: Configuration) -> None:
        """Initilize object variables."""
        self.config = config

    async def get_data(self) -> PTDevicesResponse:
        """Fetch device data from PTDevices server and format it."""
        # Request url: https://api.ptdevices.com/token/v1/device/{deviceId}?api_token={given_token}
        # Where
        #   {deviceId} is the numeric internal device id,
        #       found in the url https://www.ptdevices.com/device/level/{deviceId}
        #   {given_token} is the access token you were given

        url = f"{self.config.url}{self.config.device_id}?api_token={self.config.auth_token}"

        LOGGER.debug(
            "Sending request to %s for data from device #%s",
            self.config.url,
            self.config.device_id,
        )

        async with self.config.session.request(
            "get",
            url,
            allow_redirects=False,
        ) as results:
            LOGGER.debug(
                "%s Received from %s",
                results.status,
                self.config.url,
            )

            # Check return code
            if results.status == HTTPStatus.UNAUTHORIZED:  # 401
                raise PTDevicesUnauthorizedError(
                    f"Request to {url.split('?api_token')[0]} failed, the token provided is not valid"
                )
            elif results.status == HTTPStatus.FOUND:  # 302
                # Back end currently returns a 302 when request is not authorized
                raise PTDevicesUnauthorizedError(
                    f"Request to {url.split('?api_token')[0]} failed, the token provided is not valid (302)"
                )

            elif results.status == HTTPStatus.FORBIDDEN:  # 403
                raise PTDevicesForbiddenError(
                    f"Request to {url.split('?api_token')[0]} failed, token invalid for device {self.config.device_id}"
                )

            elif results.status != HTTPStatus.OK:  # anything but 200
                raise PTDevicesRequestError(
                    f"Request to {url.split('?api_token')[0]} failed, got unexpected response from server ({results.status})"
                )

            # Check content type
            elif (
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
