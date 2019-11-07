from subprocess import check_output

from mallennlp.domain.sys_info import SysInfo, GpuInfo


class SysInfoService:
    query = [
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
    def get_query_output(cls) -> str:
        return check_output(cls.query, universal_newlines=True)

    @classmethod
    def get(cls) -> SysInfo:
        info = SysInfo()
        try:
            output = cls.get_query_output()
            devices = [l.strip() for l in output.strip().split("\n")]
            info.gpus = []
            for device in devices:
                values = device.split(", ")
                info.driver_version = values[2]
                info.gpus.append(
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
        except FileNotFoundError:
            # `nvidia-smi` doesn't exit.
            pass
        return info
