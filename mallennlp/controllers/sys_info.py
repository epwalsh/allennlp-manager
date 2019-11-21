from typing import List, Any, Dict, Optional, Tuple

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from mallennlp.exceptions import CudaUnavailableError
from mallennlp.domain.sys_info import SysInfo, GpuInfo
from mallennlp.services import sys_info as sys_info_service
from mallennlp.services.cache import cache


@cache.memoize(timeout=60)
def retrieve_sys_info() -> SysInfo:
    return sys_info_service.get_sys_info()


@cache.memoize(timeout=1)
def retrieve_gpu_info() -> Tuple[Optional[str], Optional[List[GpuInfo]]]:
    return sys_info_service.get_gpu_info()


def retrieve_platform_components(info: SysInfo) -> List[Any]:
    info = retrieve_sys_info()
    components: List[Any] = [dcc.Markdown(f"**Platform:** `{info.platform}`")]
    if not info.gpus or not info.driver_version:
        components.extend(
            [html.Br(), dbc.Alert("No GPU devices available", color="danger")]
        )
        return components
    components.append(
        dcc.Markdown(
            f"""
**Nvidia driver version:** `{info.driver_version}`

**CUDA version:** `{info.cuda_version}`

**GPU devices available:** `{len(info.gpus)}`
            """.strip()
        )
    )
    return components


def get_gpu_device_dropdown(info: SysInfo):
    options = [
        {
            "label": f"[{gpu.id}] {gpu.name}, {gpu.mem_capacity} {gpu.mem_units}",
            "value": gpu.id,
        }
        for gpu in info.gpus or []
    ]
    if info.gpus and len(info.gpus) > 1:
        options.insert(0, {"label": "All (average)", "value": -1})
    return dcc.Dropdown(id="device-selection", value=0, options=options)


def update_device_history(
    history: List[Dict[str, int]], device_id: int
) -> Tuple[List[Dict[str, int]], Optional[GpuInfo]]:
    _, gpus = retrieve_gpu_info()
    if not gpus:
        raise CudaUnavailableError
    if device_id == -1:
        # Average across all devices.
        gpu = None
        mem = int(sum(100 * (x.mem_usage / x.mem_capacity) for x in gpus) / len(gpus))
        util = int(sum(x.utilization for x in gpus) / len(gpus))
    else:
        gpu = gpus[device_id]
        mem = int(100 * (gpu.mem_usage / gpu.mem_capacity))
        util = gpu.utilization
    history.pop(0)
    history.append({"mem": mem, "util": util})
    return history, gpu


def render_device_info(device: GpuInfo):
    return dcc.Markdown(
        f"""
**Memory**: `{device.mem_usage} / {device.mem_capacity} {device.mem_units}`

**GPU Utilization**: `{device.utilization}%`

**Fan Speed**: `{device.fan}%`

**Temperature**: `{device.temp}{device.temp_units}`
        """.strip()
    )


def render_device_util_plot(history: List[Dict[str, int]], device_id: Optional[int]):
    return {
        "data": [
            {
                "name": "Memory",
                "x": list(range(len(history))),
                "y": [y["mem"] for y in history],
                "text": [f"{y['mem']}%" for y in history],
                "hoverinfo": "text",
                "mode": "lines",
                "line": {"color": "rgb(58,74,101)", "shape": "hv"},
            },
            {
                "name": "GPU",
                "x": list(range(len(history))),
                "y": [y["util"] for y in history],
                "text": [f"{y['util']}%" for y in history],
                "hoverinfo": "text",
                "mode": "lines",
                "line": {"color": "rgb(114,192,185)", "shape": "hv"},
            },
        ],
        "layout": {
            "clickmode": "event+select",
            "xaxis": {
                "range": [0, len(history) - 1],
                "tickvals": list(range(0, len(history))),
                "ticktext": ["" for i in range(0, len(history))],
            },
            "yaxis": {"range": [0, 100]},
            "margin": {"l": 40, "b": 30, "t": 20, "pad": 2},
            "uirevision": True,
        },
    }
