from collections import OrderedDict

from dash.exceptions import PreventUpdate
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
from flask_login import current_user

from mallennlp.dashboard.components import SidebarEntry, SidebarLayout
from mallennlp.dashboard.page import Page
from mallennlp.services.url_parse import from_url
from mallennlp.services.user import MIN_PASSWORD_LENGTH, UserService
from mallennlp.services.serialization import serializable


@Page.register("/settings")
class SettingsPage(Page):
    @from_url
    @serializable
    class Params:
        active: str = "change-pw"

    _sidebar_entries = OrderedDict(
        [
            (
                "change-pw",
                SidebarEntry(
                    "Change password",
                    [
                        dbc.Form(
                            [
                                dbc.FormGroup(
                                    [
                                        dbc.Input(
                                            placeholder="Enter current password",
                                            type="password",
                                            id="settings-current-pw",
                                        )
                                    ],
                                    row=False,
                                ),
                                dbc.FormGroup(
                                    [
                                        dbc.Input(
                                            placeholder="Enter new password",
                                            type="password",
                                            id="settings-new-pw",
                                        ),
                                        dbc.FormText(
                                            f"New password must be at least {MIN_PASSWORD_LENGTH} characters long."
                                        ),
                                        dbc.FormFeedback(
                                            "Wow! That looks like a great password :)",
                                            id="settings-new-pw-valid-feedback",
                                            valid=True,
                                        ),
                                        dbc.FormFeedback(
                                            id="settings-new-pw-invalid-feedback",
                                            valid=False,
                                        ),
                                    ],
                                    row=False,
                                ),
                                dbc.FormGroup(
                                    [
                                        dbc.Input(
                                            placeholder="Confirm new password",
                                            type="password",
                                            id="settings-confirm-new-pw",
                                        ),
                                        dbc.FormFeedback(
                                            "Doesn't match :(",
                                            id="settings-confirm-new-pw-invalid-feedback",
                                            valid=False,
                                        ),
                                    ],
                                    row=False,
                                ),
                                dbc.Button(
                                    "Save",
                                    n_clicks=0,
                                    id="settings-save-new-pw",
                                    disabled=True,
                                    color="primary",
                                ),
                            ]
                        )
                    ],
                ),
            ),
            ("notifications", SidebarEntry("Notifications", ["Coming soon"])),
        ]
    )

    def get_elements(self):
        return SidebarLayout("Settings", self._sidebar_entries, self.p.active)

    def get_notifications(self):
        return [
            dbc.Toast(
                "Password successfully changed. Please log out and then log back in.",
                header="Success",
                icon="success",
                duration=4000,
                id="settings-pw-change-success",
                is_open=False,
                dismissable=True,
            ),
            dbc.Toast(
                "The current password you entered is wrong",
                header="Oops!",
                icon="danger",
                duration=4000,
                id="settings-pw-change-fail",
                is_open=False,
                dismissable=True,
            ),
        ]

    @staticmethod
    @Page.callback(
        [
            Output("settings-new-pw", "valid"),
            Output("settings-new-pw", "invalid"),
            Output("settings-new-pw-invalid-feedback", "children"),
        ],
        [Input("settings-new-pw", "value")],
    )
    def validate_new_password(value):
        if not value:
            return False, False, None
        valid, feedback = UserService.validate_password(value)
        if feedback:
            feedback = "New " + feedback
        return valid, not valid, feedback

    @staticmethod
    @Page.callback(
        [
            Output("settings-confirm-new-pw", "valid"),
            Output("settings-confirm-new-pw", "invalid"),
        ],
        [Input("settings-confirm-new-pw", "value")],
        [State("settings-new-pw", "value")],
    )
    def confirm_new_password(value1, value2):
        if not value1 or not value2:
            return False, False
        if value1 != value2:
            return False, True
        return True, False

    @staticmethod
    @Page.callback(
        [Output("settings-save-new-pw", "disabled")],
        [
            Input("settings-current-pw", "value"),
            Input("settings-new-pw", "valid"),
            Input("settings-confirm-new-pw", "valid"),
        ],
    )
    def enable_save_button(current_pw, new_is_valid, confirmed_new_is_valid):
        if not current_pw or not new_is_valid or not confirmed_new_is_valid:
            return True
        return False

    @staticmethod
    @Page.callback(
        [
            Output("settings-pw-change-success", "is_open"),
            Output("settings-pw-change-fail", "is_open"),
        ],
        [Input("settings-save-new-pw", "n_clicks")],
        [State("settings-current-pw", "value"), State("settings-new-pw", "value")],
    )
    def change_pw(n_clicks, current, new):
        if not n_clicks or not current or not new:
            raise PreventUpdate
        if not UserService.check_password(current_user, current):
            return False, True
        user_service = UserService()
        user_service.changepw(current_user.username, new)
        return True, False
