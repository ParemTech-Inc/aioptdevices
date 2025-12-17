"""Mock API for testing package."""

from typing import Any

from aiohttp import RequestInfo, web

# Configs
API_URL: str = "/token/v1"  # Token API URL
TOKEN: str = "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b"  # fake token for testing

# Device IDs
NORMAL_DEVICE_ID: str = "200"  # Always returns OK (200) and a good body
NORMAL_DEVICE_MAC: str = "123456789ABC"
EMPTY_ERROR_DEVICE_ID: str = "0"  # Always returns an empty (200)
WRONG_CONTENT_TYPE_DEVICE_ID: str = "199"  # Same as NORMAL but wrong content type
UNAUTHORIZED_ERROR_DEVICE_ID: str = "401"  # Always Returns an UNAUTHORIZED (401)
REDIRECT_ERROR_DEVICE_ID: str = "302"  # Always Returns an FOUND (302)
FORBIDDEN_ERROR_DEVICE_ID: str = "403"  # Always Returns a FORBIDDEN (403)
BAD_GATEWAY_ERROR_DEVICE_ID: str = "502"  # Always Returns a BAD_GATEWAY (502)

# Responses
GOOD_RESP: str = '{"data":{"id":200,"device_id":"123456789ABC","share_id":"fFAa523e","created":"Jul 11th 2024, 7:44 PM","user_id":1234,"device_type":"level","title":"Test Response Level","version":"100","lat":null,"lng":null,"address":null,"status":"Working","delivery_notes":null,"units":"Metric","reported":"Jul 15th, 1:25 PM","tx_reported":"Jul 15th, 8:17 AM","last_updated_on":null,"wifi_signal":"100%","tx_signal":"-46.00dBm","device_data":{"percent_level":50,"battery_voltage":6.6,"battery_status":"Good","volume_level":100,"inch_level":10,"enclosure_temperature":22.2},"device_setup":{"depth":10,"power_x":30,"power_y":3048,"power_z":24,"shape":"rectangle","diameter":null,"width":null,"length":null},"temperature_units":"C"}}'

GOOD_RESP_DICT: dict[str, Any] = {
    "123456789ABC": {
        "id": 200,
        "device_id": "123456789ABC",
        "share_id": "fFAa523e",
        "created": "Jul 11th 2024, 7:44 PM",
        "user_id": 1234,
        "device_type": "level",
        "title": "Test Response Level",
        "version": "100",
        "lat": None,
        "lng": None,
        "address": None,
        "status": "Working",
        "delivery_notes": None,
        "units": "Metric",
        "reported": "Jul 15th, 1:25 PM",
        "tx_reported": "Jul 15th, 8:17 AM",
        "last_updated_on": None,
        "wifi_signal": "100%",
        "tx_signal": "-46.00dBm",
        "device_data": {
            "percent_level": 50,
            "battery_voltage": 6.6,
            "battery_status": "Good",
            "volume_level": 100,
            "inch_level": 10,
            "enclosure_temperature": 22.2,
        },
        "device_setup": {
            "depth": 10,
            "power_x": 30,
            "power_y": 3048,
            "power_z": 24,
            "shape": "rectangle",
            "diameter": None,
            "width": None,
            "length": None,
        },
        "temperature_units": "C",
    }
}


async def good_response(request: RequestInfo) -> web.Response:
    """Return an OK (200)."""
    assert request.url.query.get("api_token") == TOKEN  # Verify the token is matching

    return web.Response(status=200, content_type="application/json", body=GOOD_RESP)


async def empty_response(request: RequestInfo) -> web.Response:
    """Return an empty response (200)."""
    assert request.url.query.get("api_token") == TOKEN  # Verify the token is valid

    return web.Response(status=200, content_type="application/json", body="")


async def content_type_invalid_response(request: RequestInfo) -> web.Response:
    """Return an OK (200) with the wrong content type."""
    return web.Response(status=200, body=GOOD_RESP)


async def unauthorized_response(requsest: RequestInfo) -> web.Response:
    """Return an UNAUTHORIZED (401) to any request."""
    return web.Response(status=401)


async def forbidden_response(requsest: RequestInfo) -> web.Response:
    """Return an UNAUTHORIZED (403) to any request."""
    return web.Response(status=403)


async def bad_gateway_response(requsest: RequestInfo) -> web.Response:
    """Return an UNAUTHORIZED (502) to any request."""
    return web.Response(status=502)


async def not_found_response(request: RequestInfo) -> web.Response:
    """Return a PAGE NOT FOUND (404) to any request."""
    return web.Response(status=404)


async def redirect_response(request: RequestInfo) -> web.Response:
    """Return a PAGE NOT FOUND (302) to any request."""
    return web.Response(status=302)
