from typing import Optional, List

import attr


@attr.s(auto_attribs=True, kw_only=True)
class GpuInfo:
    id: int
    """
    GPU ID.
    """

    name: str
    """
    GPU name (ex. GeForce GTX 1070).
    """

    mem_usage: int
    """
    Memory usage (in MiB by default).
    """

    mem_capacity: int
    """
    Memory capacity (in MiB by default).
    """

    mem_units: str = "MiB"

    utilization: int
    """
    Percent GPU utilization.
    """

    temp: int
    """
    Device temperature in celcius.
    """

    temp_units: str = "°C"

    fan: int
    """
    Percent fan utilization.
    """


@attr.s(auto_attribs=True)
class SysInfo:
    platform: str
    driver_version: Optional[str] = None
    cuda_version: Optional[str] = None
    gpus: Optional[List[GpuInfo]] = None
