from typing import List, Any, Dict

import dash_core_components as dcc

from mallennlp.services.sys_info import SysInfoService


def retrieve_sys_info():
    return SysInfoService.get()


def retrieve_sys_info_components() -> List[Any]:
    info = retrieve_sys_info()
    if not info.gpus or not info.driver_version:
        return ["No GPUs available"]
    return [
        dcc.Markdown(
            f"""
**Platform:** `{info.platform}`

**Nvidia driver version:** `{info.driver_version}`

**GPU devices available:** `{len(info.gpus)}`

---

Show GPU utilization for:
            """.strip()
        ),
        dcc.Dropdown(
            id="device-selection",
            value=-1,
            options=[{"label": "All (average)", "value": -1}]
            + [
                {
                    "label": f"[{gpu.id}] {gpu.name}, {gpu.mem_capacity} MiB",
                    "value": gpu.id,
                }
                for gpu in info.gpus
            ],
        ),
    ]


def render_device_util_plot(history: List[Dict[str, int]], device_id):
    latest = retrieve_sys_info()
    if device_id == -1:
        # Average across all devices.
        mem = int(
            sum(100 * (x.mem_usage / x.mem_capacity) for x in latest.gpus)
            / len(latest.gpus)
        )
        util = int(sum(x.utilization for x in latest.gpus) / len(latest.gpus))
    else:
        gpu = latest.gpus[device_id]
        mem = int(100 * (gpu.mem_usage / gpu.mem_capacity))
        util = gpu.utilization
    history.pop(0)
    history.append({"mem": mem, "util": util})
    return (
        dcc.Graph(
            id="gpu-util-plot",
            figure={
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
                    #  "title": "Device Utilization",
                    "clickmode": "event+select",
                    "xaxis": {
                        "range": [0, len(history) - 1],
                        "tickvals": list(range(0, len(history))),
                        "ticktext": ["" for i in range(0, len(history))],
                    },
                    "yaxis": {"range": [0, 100]},
                },
            },
        ),
    )
