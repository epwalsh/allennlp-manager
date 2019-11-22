from collections import OrderedDict
import time

import attr
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from flask_login import login_user, current_user

from mallennlp.dashboard.components import SidebarEntry, SidebarLayout
from mallennlp.dashboard.page import Page
from mallennlp.services.user import UserService
from mallennlp.services.serialization import serializable
from mallennlp.services.url_parse import from_url


@Page.register("/login")
class LoginPage(Page):
    @from_url
    @serializable
    class Params:
        next_pathname: str = attr.ib(
            default="/", converter=lambda p: "/" if p == "/login" else p  # type: ignore
        )
        next_params: str = attr.ib(
            default="?_refresh=true",
            converter=lambda p: p if p else "?_refresh=true",  # type: ignore
        )
        active: str = "sign-in"

    def get_sign_in_elements(self):
        return [
            dcc.Location(id="login-url", refresh=True),
            dbc.Form(
                [
                    dbc.FormGroup(
                        [
                            dbc.Label(
                                "Username:", html_for="login-username-input", width=2
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
                                "Password:", html_for="login-password-input", width=2
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
            ),
        ]

    def get_elements(self):
        return SidebarLayout(
            "Sign in",
            OrderedDict(
                [("sign-in", SidebarEntry("Sign in", self.get_sign_in_elements()))]
            ),
            self.p.active,
            self.p.to_dict(),
        )

    def get_notifications(self):
        return [html.Div(id="login-state")]

    @staticmethod
    @Page.callback(
        Output("login-button", "disabled"),
        [
            Input("login-username-input", "value"),
            Input("login-password-input", "value"),
        ],
    )
    def update_login_button(username, password):
        if current_user.is_authenticated:
            return True
        return not all([username, password])

    @staticmethod
    @Page.callback(
        [Output("login-state", "children")],
        [Input("login-button", "n_clicks")],
        [
            State("login-username-input", "value"),
            State("login-password-input", "value"),
        ],
    )
    def try_log_in(n_clicks, username, password):
        if current_user.is_authenticated:
            return dbc.Toast(
                "You are already logged in",
                id="login-state-notification",
                header="Success",
                icon="success",
            )
        if not n_clicks or not username or not password:
            raise PreventUpdate
        user = UserService().find(username, password)
        if user:
            login_user(user)
            return dbc.Toast(
                f"Welcome, {user.username}!",
                id="login-state-notification",
                header="Success",
                icon="success",
            )
        return dbc.Toast(
            "Invalid username or password",
            id="login-state-notification",
            header="Error",
            dismissable=True,
            duration=4000,
            icon="danger",
        )

    @Page.callback(
        [
            Output("url", "pathname"),
            Output("login-url", "pathname"),
            Output("login-url", "search"),
        ],
        [Input("login-state", "children")],
        [State("login-button", "n_clicks")],
        mutating=False,
    )
    def redirect(self, state, n_clicks):
        if (not state and not n_clicks) or not current_user.is_authenticated:
            raise PreventUpdate
        time.sleep(1)
        next_pathname = self.p.next_pathname
        next_params = self.p.next_params
        if "_refresh=true" not in next_params:
            next_params = next_params + "&_refresh=true"
        return next_pathname, next_pathname, next_params
