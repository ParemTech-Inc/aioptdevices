"""Python Library for communicating with PTDevices."""

import asyncio
from collections.abc import Collection
from enum import StrEnum
from http import HTTPStatus
import logging
from string import ascii_letters
from typing import Any, Required, TypedDict

import orjson

from aioptdevices.errors import (
    PTDevicesForbiddenError,
    PTDevicesParseError,
    PTDevicesRequestError,
    PTDevicesUnauthorizedError,
)

from .configuration import Configuration

LOGGER = logging.getLogger(__name__)

type PTDevicesResponseData = dict[str, dict[str, Any]]


class PTDevicesResponse(TypedDict, total=False):
    """Typed Response from PTDevices."""

    body: Required[dict[str, dict[str, Any]]]
    code: Required[int]
    # Ids of devices that were in the response but failed to parse. They are not
    # included in body.
    failed: set[str]


class PTDevicesBatteryState(StrEnum):
    """Store keys for hte different battery_status states."""

    UNKNOWN = "unknown"
    GOOD = "good"
    LOW = "low"


_battery_value_translations: dict[int, str] = {
    1: PTDevicesBatteryState.GOOD,
    2: PTDevicesBatteryState.LOW,
}


class PTDevicesStatusStates(StrEnum):
    """Store keys for the different device_status states."""

    UNKNOWN = "unknown"
    WORKING = "working"
    NOT_CONNECTED_YET = "not_connected_yet"
    NOT_CONNECTED = "not_connected"
    TRANSMITTER_NOT_REPORTING = "transmitter_not_reporting"
    PRESS_TRANSMITTER_CONNECT_BUTTON = "press_transmitter_connect_button"
    POWER_INTERNET_OUT_OR_RECEIVER_NOT_WORKING = (
        "power_internet_out_or_receiver_not_working"
    )


_status_value_translations: dict[int, str] = {
    0: PTDevicesStatusStates.NOT_CONNECTED_YET,
    1: PTDevicesStatusStates.NOT_CONNECTED_YET,
    2: PTDevicesStatusStates.WORKING,
    3: PTDevicesStatusStates.NOT_CONNECTED,
    4: PTDevicesStatusStates.TRANSMITTER_NOT_REPORTING,
    5: PTDevicesStatusStates.POWER_INTERNET_OUT_OR_RECEIVER_NOT_WORKING,
    6: PTDevicesStatusStates.PRESS_TRANSMITTER_CONNECT_BUTTON,
}

_convert_to_number_keys: dict[str, type] = {
    "wifi_signal": int,
    "tx_signal": float,
    "percent_level": float,
    "battery_voltage": float,
    "volume_level": float,
    "inch_level": float,
    "probe_temperature": float,
}


# Keys the Home Assistant integration needs to identify a device. A device missing any
# of these fails to parse and is reported in PTDevicesResponse["failed"].
_required_keys: tuple[str, ...] = (
    "id",
    "user_id",
    "device_type",
    "title",
    "version",
)


class _ParseIssueLog:
    """Log each parse issue at warning level once, then at debug until it is resolved.

    An issue is a (device_id, key) pair, where key "*" means the whole device failed.
    The API is polled regularly, so without this a field that is always malformed
    would log a warning on every poll.
    """

    def __init__(self) -> None:
        """Initialize with no active issues."""
        self._active: set[tuple[str, str]] = set()
        self._seen: set[tuple[str, str]] = set()

    def issue(
        self,
        device_id: str,
        key: str,
        msg: str,
        *args: Any,
        exc_info: bool = False,
    ) -> None:
        """Log a parse issue, at warning level only the first time it is seen.

        exc_info only adds the traceback to the first warning, not the repeats.
        """
        issue = (device_id, key)
        self._seen.add(issue)
        repeat = issue in self._active
        LOGGER.log(
            logging.DEBUG if repeat else logging.WARNING,
            msg,
            *args,
            exc_info=exc_info and not repeat,
        )

    def end_poll(self, parsed_device_ids: Collection[str]) -> None:
        """Finish a poll, logging issues that are resolved.

        Issues for devices that are no longer in the response are dropped silently.
        """
        for device_id, key in sorted(self._active - self._seen):
            if device_id in parsed_device_ids:
                LOGGER.info(
                    "Device %s: %s parsed successfully again",
                    device_id,
                    "device" if key == "*" else key,
                )
        self._active = self._seen
        self._seen = set()


# Parsing a device is kept together in one function on purpose: reading the packet top
# to bottom is more readable than splitting it into a dozen little functions, so the
# complexity check is disabled here.
def _parse_device(device: dict[str, Any], log: _ParseIssueLog) -> dict[str, Any]:  # noqa: C901
    """Parse a single flattened device.

    Raises KeyError if a required key is missing.
    """
    for key in _required_keys:
        if key not in device:
            raise KeyError(key)

    # Translate the device status number
    if device.get("status_number") in _status_value_translations:
        device["status"] = str(_status_value_translations[device["status_number"]])
    else:
        device["status"] = str(PTDevicesStatusStates.UNKNOWN)

    # Translate the battery status number
    if device.get("battery_status_number") is not None:
        if device["battery_status_number"] in _battery_value_translations:
            device["battery_status"] = str(
                _battery_value_translations[device["battery_status_number"]]
            )
        else:
            device["battery_status"] = str(
                PTDevicesBatteryState.UNKNOWN
            )  # TODO tests dont cover this

    # Change all measurements to float | int | str
    for key in _convert_to_number_keys:
        if device.get(key) is not None and isinstance(device.get(key), str):
            try:
                device[key] = _convert_to_number_keys[key](
                    device.get(key, "").strip(ascii_letters + "%"),
                )
            except ValueError:
                # Keep the rest of the device, only this field is unknown
                log.issue(
                    str(device.get("device_id")),
                    key,
                    "Device %s: could not parse %s=%r as %s, setting it to None",
                    device.get("device_id"),
                    key,
                    device[key],
                    _convert_to_number_keys[key].__name__,
                )
                device[key] = None

    # Pass the version through exactly as received, only making sure it is a string
    if device["version"] is not None:
        device["version"] = str(device["version"])

    # Change the inch_level to depth_level and convert to metric (meters)
    if "inch_level" in device:
        inch_level = device.pop("inch_level")
        device["depth_level"] = (
            round(0.0254 * float(inch_level), 6) if inch_level is not None else None
        )

    if device.get("volume_level") is not None:
        volume_factor = {"US Imperial": 3.785411784, "British Imperial": 4.54609}.get(
            device.get("units", "")
        )
        if volume_factor is not None:
            device["volume_level"] = round(
                volume_factor * float(device["volume_level"]), 6
            )

    if device.get("probe_temperature") is not None:
        if device.get("temperature_units", "") == "F":
            device["probe_temperature"] = round(
                (float(device.get("probe_temperature", 0.0)) - 32) * 0.5555555556, 3
            )

    return device


def _format_data(
    input: list[dict[str, Any]],
    log: _ParseIssueLog,
) -> tuple[dict[str, dict[str, Any]], set[str]]:
    """Format the returned data into a more helpful form. This includes putting id's as keys and flattening the dict.

    Returns the parsed devices and the ids of devices that failed to parse. Raises
    PTDevicesParseError if the response contained devices but none of them parsed.
    """
    output: dict[str, dict[str, Any]] = {}

    # Add id's as keys
    devices: dict[str, dict[str, Any]] = {}
    for device in input:
        if not device.get("device_id"):
            log.issue(
                f"id={device.get('id')}",
                "device_id",
                "Skipping device without a device_id (id=%s)",
                device.get("id"),
            )
            continue
        devices[device["device_id"]] = device

    # Flatten the dict

    # Recurse through key value pairs and convert from nested to flat
    def recurse(sub_dict: dict[str, dict[str, Any]]) -> dict[str, Any]:
        results: dict[str, Any] = {}

        for key, value in sub_dict.items():
            if isinstance(value, dict):
                results = {**results, **recurse(value)}
            else:
                results[key] = value

        return results

    for device_id, device in devices.items():
        output[device_id] = recurse(device)

    # At this point the data has been transformed into a flat dict
    # {"id":{...info...},"id2":{...info...}}

    failed: set[str] = set()
    for device_id, device in list(output.items()):
        try:
            output[device_id] = _parse_device(device, log)
        except (KeyError, ValueError, TypeError, AttributeError):
            log.issue(
                device_id,
                "*",
                "Device %s: failed to parse, skipping",
                device_id,
                exc_info=True,
            )
            output.pop(device_id)
            failed.add(device_id)

    log.end_poll(output.keys())

    if input and not output:
        raise PTDevicesParseError(
            f"Failed to parse any of the {len(input)} device(s) in the response"
        )

    return output, failed


class Interface:
    """Interface for PTDevices."""

    def __init__(self, config: Configuration) -> None:
        """Initilize object variables."""
        self.config = config
        self._parse_log = _ParseIssueLog()

    async def get_data(self) -> PTDevicesResponse:
        """Fetch device data from PTDevices server and format it."""
        # Request url: https://api.ptdevices.com/token/v1/device/{deviceId}?api_token={given_token}
        # Where
        #   {deviceId} is the numeric internal device id,
        #       found in the url https://www.ptdevices.com/device/level/{deviceId}
        #   {given_token} is the access token you were given
        #
        # Request url: https://api.ptdevices.com/token/v1/devices?api_token={given_token}
        # Where
        #   {given_token} is the access token you were given

        # Construct the URL differently for multi device and single device requests
        if self.config.device_id == "*":
            url = f"{self.config.url}/devices?api_token={self.config.auth_token}"
            LOGGER.debug(
                "Sending request to %s for data from all devices",
                self.config.url,
            )
        else:
            url = f"{self.config.url}/device/{self.config.device_id}?api_token={self.config.auth_token}"
            LOGGER.debug(
                "Sending request to %s for data from device %s",
                self.config.url,
                self.config.device_id,
            )

        try:
            async with asyncio.timeout(10):
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
                    if results.status == HTTPStatus.FOUND:  # 302
                        # Back end currently returns a 302 when request is not authorized
                        raise PTDevicesUnauthorizedError(
                            f"Request to {url.split('?api_token')[0]} failed, the token provided is not valid (302)"
                        )

                    if results.status == HTTPStatus.FORBIDDEN:  # 403
                        raise PTDevicesForbiddenError(
                            f"Request to {url.split('?api_token')[0]} failed, token invalid for device {self.config.device_id}"
                        )

                    if results.status != HTTPStatus.OK:  # anything but 200
                        raise PTDevicesRequestError(
                            f"Request to {url.split('?api_token')[0]} failed, got unexpected response from server ({results.status})"
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

                    try:
                        data = orjson.loads(raw_json)["data"]
                    except (orjson.JSONDecodeError, KeyError, TypeError) as err:
                        raise PTDevicesParseError(
                            f"Failed to parse response from {url.split('?api_token')[0]}: {err!r}"
                        ) from err

                    formatted_data, failed = _format_data(
                        data if type(data) is list else [data],
                        self._parse_log,
                    )

                    # Store the new data to the response and return
                    return PTDevicesResponse(
                        code=results.status, body=formatted_data, failed=failed
                    )

        except TimeoutError as err:
            # If the request timed out, throw a request error
            raise PTDevicesRequestError(
                f"Request to {url.split('?api_token')[0]} failed, request timed out"
            ) from err
