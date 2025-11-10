"""CLI for PTDevices."""

import argparse
import asyncio
from asyncio.timeouts import timeout
import logging

from aiohttp import ClientSession, CookieJar

import aioptdevices
from aioptdevices.configuration import Configuration
from aioptdevices.interface import Interface

LOGGER = logging.getLogger(__name__)


async def connect(
    deviceID: str, authToken: str, url: str, webSession: ClientSession
) -> Interface | None:
    """Set up and Connect to PTDevices."""

    # Setup interface to PTDevices
    interface: Interface = Interface(
        Configuration(authToken, deviceID, url, webSession)
    )
    try:
        async with timeout(10):
            data = await interface.get_data()
            LOGGER.info("Data: %s", data.get("body"))
    except aioptdevices.PTDevicesRequestError as err:
        LOGGER.warning("failed to connect to PTDevices server: %s", err)

    except aioptdevices.PTDevicesUnauthorizedError as err:
        LOGGER.warning("Unable to read device data because of bad token: %s", err)

    except aioptdevices.PTDevicesForbiddenError as err:
        LOGGER.warning("Unable, device does not belong to the token holder: %s", err)
    else:
        return interface
    return None


async def main(
    deviceID: str,
    authToken: str,
    url: str,
) -> None:
    """Configure a connection and get the token api data from server."""

    # ----------  Connecting To PTDevices  -----------

    LOGGER.info(
        "\n%s\n", "  Connecting To PTDevices  ".center(48, "-")
    )  # Output a section title for connecting

    # Create a web session for use when connecting
    session: ClientSession = ClientSession(cookie_jar=CookieJar(unsafe=True))
    # session = ClientSession()

    # Setup connection to PTDevices
    ptdevicesInterface = await connect(deviceID, authToken, url, session)

    if not ptdevicesInterface:  # Failed connection to PTDevices
        LOGGER.error("Failed to connect to PTDevices")
        await session.close()
        return

    # -----------------  Connected  ------------------

    LOGGER.info(
        "\n%s\n", "  Connected  ".center(48, "-")
    )  # Output a section title when connected
    LOGGER.info("Successfully connected to %s", deviceID)

    # try:
    #     data = await ptdevicesInterface.get_data()
    #     LOGGER.info(f"Device {deviceID} data: \n{data}")
    # except aioptdevices.PTDevicesRequestError as err:
    #     LOGGER.warning(f"failed to connect to PTDevices server: {err}")

    # except aioptdevices.PTDevicesUnauthorizedError as err:
    #     LOGGER.warning(f"Unable, to read device data because of bad token: {err}")

    # except aioptdevices.PTDevicesForbiddenError as err:
    #     LOGGER.warning(f"Unable, device does not belong to the token holder: {err}")

    await session.close()
    return


def starter():
    """Parse CLI Arguments and fetch device data."""
    default_url = "https://www.ptdevices.com/token/v1/device/"

    # Parse cli args
    parser = argparse.ArgumentParser()
    parser.add_argument("deviceID", type=int)
    parser.add_argument("authToken", type=str)
    parser.add_argument("-U", "--url", type=str, default=default_url)
    parser.add_argument("-D", "--debug", action="store_true")
    args = parser.parse_args()

    # Set the log level
    LOG_LEVEL = logging.INFO
    if args.debug:
        LOG_LEVEL = logging.DEBUG

    logging.basicConfig(format="%(message)s", level=LOG_LEVEL)

    # Output the settings
    # LOGGER.info(
    #     f"deviceID: {args.deviceID}\nToken: {args.authToken}\nurl: {args.url}\ndebug: {args.debug}\n"
    # )

    # --------------------  ARGS  --------------------

    LOGGER.info("\n%s\n", "  ARGS  ".center(48, "-"))  # Output a section title for args
    LOGGER.info("deviceID: %s", args.deviceID)
    # LOGGER.info("Token: %s", args.authToken)
    LOGGER.info("url: %s", args.url)
    LOGGER.info("debug: %s", args.debug)

    # Run the program
    try:
        asyncio.run(
            main(
                deviceID=args.deviceID,
                authToken=args.authToken,
                url=args.url,
            )
        )

    except KeyboardInterrupt:
        LOGGER.info("Keyboard interrupt")


if __name__ == "__main__":
    starter()
# ----------------------  ARGS  ------------------
