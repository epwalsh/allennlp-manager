from typing import Optional, List

import attr


@attr.s(auto_attribs=True)
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
    Memory usage in MiB.
    """

    mem_capacity: int
    """
    Memory capacity in MiB.
    """

    utilization: int
    """
    Percent GPU utilization.
    """

    temp: int
    """
    Device temperature in celcius.
    """

    fan: int
    """
    Percent fan utilization.
    """


@attr.s(auto_attribs=True)
class SysInfo:
    driver_version: Optional[str] = None
    gpus: Optional[List[GpuInfo]] = None
