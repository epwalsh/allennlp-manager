import platform
import re
from subprocess import check_output
from typing import Optional, Tuple, List

import py3nvml.py3nvml as nvml

from mallennlp.domain.sys_info import SysInfo, GpuInfo


QUERY_TIMEOUT = 3

CUDA_VERSION_QUERY = ["nvidia-smi"]

CUDA_VERSION_REGEX = re.compile(r"CUDA Version:\s([0-9.]+)")


def _get_cuda_version_query_output() -> str:
    return check_output(
        CUDA_VERSION_QUERY, universal_newlines=True, timeout=QUERY_TIMEOUT
    )


def get_cuda_version() -> Optional[str]:
    try:
        output = _get_cuda_version_query_output()
        cuda_version_match = CUDA_VERSION_REGEX.search(output)
        if cuda_version_match:
            return cuda_version_match.group(1)
        return None
    except FileNotFoundError:
        # `nvidia-smi` doesn't exit.
        return None


def try_get_info(f, h, default=None):
    try:
        return f(h)
    except nvml.NVMLError_NotSupported:
        return default


def get_gpu_info() -> Tuple[Optional[str], Optional[List[GpuInfo]]]:
    """
    Get driver version and list of ``GpuInfo``, if available.
    """
    try:
        nvml.nvmlInit()
    except nvml.NVMLError:
        # Not available.
        return None, None

    driver_version: str = nvml.nvmlSystemGetDriverVersion()
    gpus: List[GpuInfo] = []

    device_count: int = nvml.nvmlDeviceGetCount()
    for i in range(device_count):
        handle = nvml.nvmlDeviceGetHandleByIndex(i)
        name = try_get_info(nvml.nvmlDeviceGetName, handle)
        fan_speed = try_get_info(nvml.nvmlDeviceGetFanSpeed, handle, default=0)
        temp = try_get_info(
            lambda h: nvml.nvmlDeviceGetTemperature(h, nvml.NVML_TEMPERATURE_GPU),
            handle,
            default=0,
        )
        mem_info = try_get_info(nvml.nvmlDeviceGetMemoryInfo, handle)
        if mem_info:
            mem_used = mem_info.used >> 20
            mem_total = mem_info.total >> 20
        else:
            mem_used = 0
            mem_total = 0
        util = try_get_info(nvml.nvmlDeviceGetUtilizationRates, handle)
        if util:
            gpu_util = util.gpu
        else:
            gpu_util = 0
        gpus.append(
            GpuInfo(
                id=i,
                name=name,
                mem_usage=mem_used,
                mem_capacity=mem_total,
                utilization=gpu_util,
                temp=temp,
                fan=fan_speed,
            )
        )

    nvml.nvmlShutdown()

    return driver_version, gpus


def get_sys_info() -> SysInfo:
    driver_version, gpus = get_gpu_info()
    return SysInfo(
        platform.platform(),
        driver_version=driver_version,
        gpus=gpus,
        cuda_version=get_cuda_version(),
    )
