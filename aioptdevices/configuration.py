"""Configuration Library"""

from dataclasses import dataclass
from aiohttp import ClientSession


@dataclass
class Configuration:
    """PTDevices Communication Configuration"""

    authToken: str  # Used for authorizing communication with server
    deviceId: int  # Used to identify the device to get data from
    url: str  # URL to get data from
    session: ClientSession  # Connection session with servers
