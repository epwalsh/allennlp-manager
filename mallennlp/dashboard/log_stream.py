from pathlib import Path

import attr
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from mallennlp.dashboard.components import element
from mallennlp.dashboard.page import Page
from mallennlp.exceptions import InvalidPageParametersError
from mallennlp.services.log_stream import LogStreamService
from mallennlp.services.serialization import serializable
from mallennlp.services.url_parse import from_url


@Page.register("/log-stream")
class LogStream(Page):
    @serializable
    class SessionState:
        stream: LogStreamService

    @from_url
    @serializable
    class Params:
        path: str = attr.ib()

        @path.validator
        def check_path_exists(self, attribute, value):
            if not Path(value).exists():
                raise InvalidPageParametersError(f"log file {value} not found")

    @classmethod
    def from_params(cls, params):
        stream = LogStreamService(params.path)
        return cls(cls.SessionState(stream=stream), params)

    def get_elements(self):
        return [
            dcc.Interval(id="log-stream-update-interval", interval=1000),
            html.H3(self.s.stream.path),
            html.Div(id="log-stream-content"),
        ]

    @Page.callback(
        [Output("log-stream-content", "children")],
        [Input("log-stream-update-interval", "n_intervals")],
    )
    def render_log_stream_content(self, _):
        lines = self.s.stream.readlines()
        content = [html.Pre(html.Code(line)) for line in lines]
        return element(content, width=True)
