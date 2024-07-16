"""Python Library for communicating with PTDevices."""

from http import HTTPStatus
import logging
from typing import Any, TypedDict

from aiohttp import client_exceptions
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

        try:
            async with self.config.session.request(
                "get",
                url,
            ) as results:
                LOGGER.debug(
                    "%s Received from %s, %s", results.status, self.config.url, results
                )

                # Check return code
                if results.status == HTTPStatus.UNAUTHORIZED:  # 401
                    raise PTDevicesUnauthorizedError(
                        f"Request to {url} failed, the token provided is not valid"
                    )

                if results.status == HTTPStatus.FORBIDDEN:  # 403
                    raise PTDevicesForbiddenError(
                        f"Request to {url} failed, token invalid for device {self.config.device_id}"
                    )

                if results.status != HTTPStatus.OK:  # anything but 200
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
            raise PTDevicesRequestError(f"Request to {url} failed: {error}") from error
