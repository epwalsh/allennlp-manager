import platform
from subprocess import check_output
from typing import Optional, Tuple, List

from mallennlp.domain.sys_info import SysInfo, GpuInfo


class SysInfoService:
    gpu_query = [
        "nvidia-smi",
        "--query-gpu="
        + ",".join(
            [
                "index",
                "name",
                "driver_version",
                "memory.used",
                "memory.total",
                "utilization.gpu",
                "temperature.gpu",
                "fan.speed",
            ]
        ),
        "--format=csv,nounits,noheader",
    ]

    @classmethod
    def get_gpu_query_output(cls) -> str:
        return check_output(cls.gpu_query, universal_newlines=True, timeout=3)

    @classmethod
    def get_gpu_info(cls) -> Tuple[Optional[str], Optional[List[GpuInfo]]]:
        try:
            driver_version = None
            gpus = []
            output = cls.get_gpu_query_output()
            devices = [l.strip() for l in output.strip().split("\n")]
            for device in devices:
                values = device.split(", ")
                driver_version = values[2]
                gpus.append(
                    GpuInfo(
                        id=int(values[0]),
                        name=values[1],
                        mem_usage=int(values[3]),
                        mem_capacity=int(values[4]),
                        utilization=int(values[5]),
                        temp=int(values[6]),
                        fan=int(values[7]),
                    )
                )
            return driver_version, sorted(gpus, key=lambda x: x.id)
        except FileNotFoundError:
            # `nvidia-smi` doesn't exit.
            return None, None

    @classmethod
    def get(cls) -> SysInfo:
        info = SysInfo(platform.platform())
        driver_version, gpus = cls.get_gpu_info()
        info.driver_version = driver_version
        info.gpus = gpus
        return info
