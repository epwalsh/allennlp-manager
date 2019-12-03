from collections import OrderedDict
from typing import List, Dict, Any, Optional

import attr
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from mallennlp.controllers.sys_info import (
    retrieve_sys_info,
    retrieve_platform_components,
    get_gpu_device_dropdown,
    render_device_util_plot,
    update_device_history,
    render_device_info,
)
from mallennlp.dashboard.components import SidebarEntry, SidebarLayout
from mallennlp.dashboard.page import Page
from mallennlp.domain.sys_info import GpuInfo
from mallennlp.exceptions import CudaUnavailableError
from mallennlp.services.serde import serde


MAX_DEVICE_HISTORY = 20


def empty_device_history():
    return [{"mem": 0, "util": 0} for _ in range(MAX_DEVICE_HISTORY)]


@Page.register("/sys-info")
class SysInfoPage(Page):
    @serde
    class SessionState:
        device_id: int = attr.ib(default=-1)
        device_info: Optional[Dict[str, Any]] = None
        device_history: List[Dict[str, int]] = attr.ib(
            default=attr.Factory(empty_device_history)
        )

    @serde
    class Params:
        active: str = "platform"

    def get_gpu_elements(self, info):
        if info.gpus:
            return [
                dcc.Interval(
                    id="sys-info-update-interval", interval=1500, n_intervals=0
                ),
                get_gpu_device_dropdown(info),
                html.Br(),
                html.Div(id="gpu-util-info"),
                dcc.Graph(id="gpu-util-plot", config={"displayModeBar": False}),
            ]
        return [html.Br(), dbc.Alert("No GPU devices available", color="danger")]

    def get_elements(self):
        info = retrieve_sys_info()
        sidebar_entries = [
            (
                "platform",
                SidebarEntry("Platform", lambda: retrieve_platform_components(info)),
            ),
            ("gpu", SidebarEntry("GPU info", lambda: self.get_gpu_elements(info))),
        ]
        return SidebarLayout(
            "System info", OrderedDict(sidebar_entries), self.p.active, self.p
        )

    @Page.callback(
        [Output("gpu-util-info", "children"), Output("gpu-util-plot", "figure")],
        [
            Input("device-selection", "value"),
            Input("sys-info-update-interval", "n_intervals"),
        ],
        mutating=True,
    )
    def render_gpu_utilization_info(self, device_id, _):
        if device_id is None:
            self.s.device_history = empty_device_history()
            return None, render_device_util_plot(self.s.device_history, device_id)
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
            return (
                render_device_info(device_info),
                render_device_util_plot(self.s.device_history, device_id),
            )
        return None, render_device_util_plot(self.s.device_history, device_id)
