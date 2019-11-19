from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_html_components as html

from mallennlp.dashboard.page import Page
from mallennlp.services.serialization import serializable
from mallennlp.services.url_parse import from_url


@Page.register("/hello-world")
class HelloWorld(Page):
    requires_login = True
    navlink_name = "Hello, World!"

    @serializable
    class SessionState:
        name: str = "World!"

    @from_url
    @serializable
    class Params:
        initial_message: str = "Hello, World!"

    def get_elements(self):
        return [
            dbc.Input(
                placeholder="Enter your name", type="text", id="hello-name-input"
            ),
            html.Br(),
            dbc.Button("Save", id="hello-name-save", color="primary"),
            html.Br(),
            dbc.Button("Say hello", id="hello-name-trigger-output", color="primary"),
            html.Br(),
            html.Div(id="hello-name-output", children=self.p.initial_message),
        ]

    @Page.callback(
        [], [Input("hello-name-save", "n_clicks")], [State("hello-name-input", "value")]
    )
    def save_name(self, n_clicks, value):
        if not n_clicks or not value:
            raise PreventUpdate
        self.s.name = value  # update SessionState

    @Page.callback(
        [Output("hello-name-output", "children")],
        [Input("hello-name-trigger-output", "n_clicks")],
        mutating=False,  # callback doesn't mutate state
    )
    def render_hello_output(self, n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return f"Hello, {self.s.name}!"
