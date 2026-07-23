from typing import Literal, Optional
from dataclasses import dataclass

PollingMode = Literal["cloud", "local"]

@dataclass(frozen=True)
class DeviceConfiguration:
    """Manages connection parameters for a PTDevices unit."""
    device_name: str
    polling_mode: PollingMode = "cloud"  # Defaulting to cloud
    api_token: Optional[str] = None      # Required for Cloud Mode
    local_ip: Optional[str] = None       # Required for Local Mode
    poll_endpoint: Optional[str] = None  # Specific endpoint (e.g., /get_sensors)