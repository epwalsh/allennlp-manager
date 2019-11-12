from typing import List, Dict, Any, Optional

import attr
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from mallennlp.controllers.sys_info import (
    retrieve_sys_info_components,
    render_device_util_plot,
    update_device_history,
    render_device_info,
)
from mallennlp.dashboard.components import element
from mallennlp.dashboard.page import Page
from mallennlp.domain.sys_info import GpuInfo
from mallennlp.exceptions import CudaUnavailableError
from mallennlp.services.serialization import serializable


MAX_DEVICE_HISTORY = 20


def empty_device_history():
    return [{"mem": 0, "util": 0} for _ in range(MAX_DEVICE_HISTORY)]


@Page.register("/sys-info")
class SysInfoPage(Page):
    @serializable
    class SessionState:
        device_id: int = attr.ib(default=-1)
        device_info: Optional[Dict[str, Any]] = None
        device_history: List[Dict[str, int]] = attr.ib(
            default=attr.Factory(empty_device_history)
        )

    def get_elements(self):
        return [
            dcc.Interval(id="sys-info-update-interval", interval=1500),
            html.H3("System Info"),
            element(
                [
                    html.Div(id="system-info", children=retrieve_sys_info_components()),
                    html.Div(id="gpu-util-info"),
                ],
                width=True,
            ),
        ]

    @Page.callback(
        [Output("gpu-util-info", "children")],
        [
            Input("device-selection", "value"),
            Input("sys-info-update-interval", "n_intervals"),
        ],
    )
    def render_gpu_utilization_info(self, device_id, _):
        if device_id is None:
            return None
        if device_id != self.s.device_id:
            self.s.device_id = device_id
            self.s.device_history = empty_device_history()
        device_info: Optional[GpuInfo] = None
        try:
            self.s.device_history, device_info = update_device_history(
                self.s.device_history, self.s.device_id
            )
        except CudaUnavailableError:
            self.s.device_history = empty_device_history()
        if device_info:
            return [
                html.Br(),
                render_device_info(device_info),
                render_device_util_plot(self.s.device_history, self.s.device_id),
            ]
        return [render_device_util_plot(self.s.device_history, self.s.device_id)]
