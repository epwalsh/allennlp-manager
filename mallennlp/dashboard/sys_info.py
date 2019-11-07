from typing import List, Dict

from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from mallennlp.controllers.sys_info import (
    retrieve_sys_info_components,
    render_device_util_plot,
)
from mallennlp.dashboard.components import element
from mallennlp.dashboard.page import Page


@Page.register("/sys-info")
class SysInfoPage(Page):
    max_device_history = 20

    def __init__(
        self,
        message: str = "hi there!",
        last_button: str = "hello",
        device_id: int = -1,
        device_history: List[Dict[str, int]] = None,
    ):
        self.message = message
        self.last_button = last_button
        self.device_id = device_id
        self.device_history = device_history or self.reset_device_history()

    @classmethod
    def reset_device_history(cls):
        return [{"mem": 0, "util": 0} for _ in range(cls.max_device_history)]

    def get_elements(self):
        return [
            dcc.Interval(id="sys-info-update-interval", interval=1000 * 1),
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
    def render_gpu_utilization_plot(self, device_id, _):
        if device_id != self.device_id:
            self.device_id = device_id
            self.device_history = self.reset_device_history()
        return render_device_util_plot(self.device_history, self.device_id)
