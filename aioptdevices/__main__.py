""" CLI for PTDevices """

import aioptdevices

import argparse
import logging
import asyncio
from aiohttp import ClientSession, CookieJar
from asyncio.timeouts import timeout
from time import sleep
from aioptdevices.interface import Interface
from aioptdevices.configuration import Configuration

LOGGER = logging.getLogger(__name__)


async def connect(
    deviceID: str, authToken: str, url: str, webSession: ClientSession
) -> Interface | None:
    """Setup and Connect to PTDevices"""

    # Setup interface to PTDevices
    interface = Interface(Configuration(authToken, deviceID, url, webSession))
    try:
        async with timeout(10):
            data = await interface.get_data()
            LOGGER.info(f"Data: {data['body']}")
        return interface
    except aioptdevices.PTDevicesRequestError as err:
        LOGGER.warning(f"failed to connect to PTDevices server: {err}")

    except aioptdevices.PTDevicesUnauthorizedError as err:
        LOGGER.warning(f"Unable, to read device data because of bad token: {err}")

    except aioptdevices.PTDevicesForbiddenError as err:
        LOGGER.warning(f"Unable, device does not belong to the token holder: {err}")
    return None


async def main(
    deviceID: str,
    authToken: str,
    url: str,
) -> None:
    LOGGER.info(
        "\n" + "  Connecting To PTDevices  ".center(48, "-") + "\n"
    )  # Output a section title for connecting

    # Create a web session for use when connecting
    session = ClientSession(cookie_jar=CookieJar(unsafe=True))
    # session = ClientSession()

    # Setup connection to PTDevices
    ptdevicesInterface = await connect(deviceID, authToken, url, session)

    if not ptdevicesInterface:  # Failed connection to PTDevices
        LOGGER.error("Failed to connect to PTDevices")
        await session.close()
        return False

    # Successful connection
    LOGGER.info(
        "\n" + "  Connected  ".center(48, "-") + "\n"
    )  # Output a section title when connected
    LOGGER.info(f"Successfully connected to {deviceID}")

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
    return True


if __name__ == "__main__":
    default_url = "https://api.ptdevices.com/token/v1/device/"

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

    LOGGER.info(
        "\n" + "  ARGS  ".center(48, "-") + "\n"
    )  # Output a section title for args

    LOGGER.info(
        f"deviceID: {args.deviceID}\n"
        f"Token: {args.authToken}\n"
        f"url: {args.url}\n"
        f"debug: {args.debug}\n"
    )

    # Run the program
    try:
        for i in range(20):
            ret = asyncio.run(
                main(
                    deviceID=args.deviceID,
                    authToken=args.authToken,
                    url=args.url,
                )
            )
            if not ret:
                LOGGER.error(f"failed at loop {i} / 20")
                break
            sleep(0.5)

    except KeyboardInterrupt:
        LOGGER.info("Keyboard interrupt")
# ----------------------  ARGS  ------------------
