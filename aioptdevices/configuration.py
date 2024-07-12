"""Configuration Library."""

from dataclasses import dataclass

from aiohttp import ClientSession


@dataclass
class Configuration:
    """PTDevices Communication Configuration."""

    auth_token: str  # Used for authorizing communication with server
    device_id: str  # Used to identify the device to get data from
    url: str  # URL to get data from
    session: ClientSession  # Connection session with servers
