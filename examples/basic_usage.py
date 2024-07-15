"""Example for basic usage."""

from aiohttp import ClientSession

from aioptdevices import Configuration, Interface, PTDevicesResponse


async def main():

    web_session = ClientSession()

    interface = Interface(
        Configuration(
            auth_token="your API token",
            device_id="your device id or mac address",
            url="https://www.ptdevices.com/token/v1/device/",
            session=web_session,
        )
    )

    data: PTDevicesResponse = await interface.get_data()

    print(
        data.get("body")
    )  # Prints the device data, see https://support.paremtech.com/portal/en/kb/articles/api-options#Token_API
