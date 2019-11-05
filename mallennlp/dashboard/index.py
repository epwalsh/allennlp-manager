from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_html_components as html

from mallennlp.dashboard.page import Page


@Page.register("/")
class IndexPage(Page):
    def __init__(self, message: str = "hi there!", last_button: str = "hello"):
        self.message = message
        self.last_button = last_button

    def get_elements(self):
        return [
            dbc.Button("Say hello", id="say-hello-button"),
            html.Br(),
            html.Div(id="hello"),
            html.Br(),
            dbc.Button("Say hello again", id="say-hello-again-button"),
            html.Br(),
            html.Div(id="hello-again"),
        ]

    @Page.callback(
        [Output("hello", "children")], [Input("say-hello-button", "n_clicks")]
    )
    def update_hello(self, n_clicks):
        self.last_button = "hello"
        return self.message + f" {n_clicks}"

    @Page.callback(
        [Output("hello-again", "children")],
        [Input("say-hello-again-button", "n_clicks")],
    )
    def update_hello_again(self, n_clicks):
        self.last_button = "hello-again"
        return "Hello again!" + f" {n_clicks}"
