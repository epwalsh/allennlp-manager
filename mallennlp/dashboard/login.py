import time
from typing import List, Dict

import attr
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from flask_login import login_user, current_user

from mallennlp.dashboard.components import element
from mallennlp.dashboard.page import Page
from mallennlp.domain.page_state import BasePageState
from mallennlp.services.user import UserService


def validate_next_params(next_params: str) -> str:
    if next_params and "_refresh=1" not in next_params:
        return next_params + "&_refresh=1"
    return "?_refresh=1"


@Page.register("/login")
class LoginPage(Page):
    @attr.s(kw_only=True, auto_attribs=True)
    class PageState(BasePageState):
        next_pathname: str = attr.ib(
            default="/", converter=lambda p: "/" if p == "/login" else p  # type: ignore
        )
        next_params: str = attr.ib(default="", converter=validate_next_params)

        @classmethod
        def from_params(cls, params: Dict[str, List[str]]):
            return cls(
                next_pathname=(params.get("next_pathname") or ["/"])[0],
                next_params=(params.get("next_params") or [""])[0],
            )

    def get_elements(self):
        return [
            dcc.Location(id="login-url", refresh=True),
            element(html.H3("Sign in"), pad=False, hover=True),
            element(
                [
                    dbc.Form(
                        [
                            dbc.FormGroup(
                                [
                                    dbc.Label(
                                        "Username:",
                                        html_for="login-username-input",
                                        width=2,
                                    ),
                                    dbc.Input(
                                        placeholder="Enter your username",
                                        type="text",
                                        id="login-username-input",
                                    ),
                                ],
                                row=False,
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label(
                                        "Password:",
                                        html_for="login-password-input",
                                        width=2,
                                    ),
                                    dbc.Input(
                                        placeholder="Enter your password",
                                        type="password",
                                        id="login-password-input",
                                    ),
                                ],
                                row=False,
                            ),
                            dbc.Button(
                                "Sign in",
                                n_clicks=0,
                                id="login-button",
                                disabled=True,
                                color="primary",
                            ),
                        ]
                    )
                ],
                width=True,
            ),
            html.Br(),
            html.Div(id="login-state"),
        ]

    @Page.callback(
        Output("login-button", "disabled"),
        [
            Input("login-username-input", "value"),
            Input("login-password-input", "value"),
        ],
    )
    def update_login_button(self, username, password):
        if current_user.is_authenticated:
            return True
        return not all([username, password])

    @Page.callback(
        [Output("login-state", "children")],
        [Input("login-button", "n_clicks")],
        [
            State("login-username-input", "value"),
            State("login-password-input", "value"),
        ],
    )
    def try_log_in(self, n_clicks, username, password):
        if current_user.is_authenticated:
            return dbc.Alert("You are already logged in", color="success")
        if not n_clicks or not username or not password:
            raise PreventUpdate
        user = UserService().find(username, password)
        if user:
            login_user(user)
            return dbc.Alert(f"Welcome, {user.username}!", color="success")
        return dbc.Alert("Invalid username or password", color="danger")

    @Page.callback(
        [
            Output("url", "pathname"),
            Output("login-url", "pathname"),
            Output("login-url", "search"),
        ],
        [Input("login-state", "children")],
        [State("login-button", "n_clicks")],
    )
    def redirect(self, state, n_clicks):
        if not state or not n_clicks or not current_user.is_authenticated:
            raise PreventUpdate
        time.sleep(1)
        next_pathname = self.s.next_pathname
        next_params = self.s.next_params
        return next_pathname, next_pathname, next_params
