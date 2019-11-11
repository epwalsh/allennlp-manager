from pathlib import Path
from typing import Dict, List

import attr
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from mallennlp.dashboard.components import element
from mallennlp.dashboard.page import Page
from mallennlp.exceptions import InvalidPageParametersError
from mallennlp.services.log_stream import LogStreamService
from mallennlp.services.serialization import Serializable


@Page.register("/log-stream")
class LogStream(Page):
    @attr.s(kw_only=True, auto_attribs=True)
    class SessionState(Serializable):
        stream: LogStreamService

    @classmethod
    def from_params(cls, params: Dict[str, List[str]]):
        try:
            path = params["path"][0]
            if not Path(path).exists():
                raise InvalidPageParametersError(f"log file {path} not found")
            stream = LogStreamService(path)
            return cls(cls.SessionState(stream=stream))
        except (IndexError, KeyError):
            raise InvalidPageParametersError("'path' parameter is required")

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
