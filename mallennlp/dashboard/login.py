from typing import List, Dict

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from flask_login import login_user, current_user

from mallennlp.dashboard.page import Page
from mallennlp.domain.user import User


@Page.register("/login")
class LoginPage(Page):
    def __init__(self, next_pathname: str = None, next_params: str = None):
        self.next_pathname = next_pathname or "/"
        if self.next_pathname == "/login":
            self.next_pathname = "/"
        if next_params:
            self.next_params = next_params + "&_refresh=1"
        else:
            self.next_params = "?_refresh=1"

    @classmethod
    def from_params(cls, params: Dict[str, List[str]]):
        return cls(
            next_pathname=(params.get("next_pathname") or ["/"])[0],
            next_params=(params.get("next_params") or [""])[0],
        )

    def get_elements(self):
        return [
            dcc.Location(id="login-url", refresh=True),
            dbc.Button("Log in", id="log-in-button"),
            html.Div(id="login-state"),
        ]

    @Page.callback(
        [Output("login-state", "children")], [Input("log-in-button", "n_clicks")]
    )
    def try_log_in(self, n_clicks):
        if current_user.is_authenticated:
            return dbc.Alert("You are already logged in", color="success")
        if not n_clicks:
            raise PreventUpdate
        user = User(0, 0, "admin", "password")
        login_user(user)
        return dbc.Alert(f"Welcome, {user.username}!", color="success")

    @Page.callback(
        [
            Output("url", "pathname"),
            Output("login-url", "pathname"),
            Output("login-url", "search"),
        ],
        [Input("login-state", "children")],
        [State("log-in-button", "n_clicks")],
    )
    def redirect(self, state, n_clicks):
        if not state or not n_clicks or not current_user.is_authenticated:
            raise PreventUpdate
        next_pathname = self.next_pathname[0]
        next_params = self.next_params[0]
        return next_pathname, next_pathname, next_params
