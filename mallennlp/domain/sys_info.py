from typing import Optional, List

from mallennlp.domain.dataclass import dataclass


@dataclass
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

    mem_units: str = "MiB"

    temp_units: str = "°C"


@dataclass
class SysInfo:
    platform: str
    driver_version: Optional[str] = None
    cuda_version: Optional[str] = None
    gpus: Optional[List[GpuInfo]] = None
