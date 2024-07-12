"""AioPTDevices Errors."""


class PTDevicesError(Exception):
    """Base Error for PTDevices."""


class PTDevicesRequestError(PTDevicesError):
    """The request was unable to be fulfilled.

    Caused by a bad url
    """


class PTDevicesUnauthorizedError(PTDevicesError):
    """The request was denied because the user does not have permission to access the device requested.

    The server did not recognize the token
    """


class PTDevicesForbiddenError(PTDevicesError):
    """The request was denied because the user does not have permission to access the device requested.

    The server recognized the token but the device is not accessible by the linked account
    """
