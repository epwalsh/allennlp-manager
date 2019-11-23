from collections import OrderedDict
import time

from dash.exceptions import PreventUpdate
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from flask_login import current_user, logout_user

from mallennlp.dashboard.components import SidebarEntry, SidebarLayout
from mallennlp.dashboard.page import Page
from mallennlp.domain.user import Permissions
from mallennlp.services.url_parse import from_url
from mallennlp.services.user import MIN_PASSWORD_LENGTH, UserService
from mallennlp.services.serialization import serializable


@Page.register("/settings")
class SettingsPage(Page):
    @from_url
    @serializable
    class Params:
        active: str = "profile"

    def get_profile_elements(self):
        return [
            html.H5("Personal details"),
            html.Hr(),
            dbc.Form(
                [
                    dbc.FormGroup(
                        [
                            dbc.Label("Full name"),
                            dbc.Input(
                                value=current_user.fullname,
                                type="text",
                                id="settings-fullname",
                            ),
                        ],
                        row=False,
                    ),
                    dbc.FormGroup(
                        [
                            dbc.Label("Nickname"),
                            dbc.Input(
                                value=current_user.nickname,
                                type="text",
                                id="settings-nickname",
                            ),
                        ],
                        row=False,
                    ),
                    dbc.FormGroup(
                        [
                            dbc.Label("Role"),
                            dbc.Input(
                                value=current_user.role,
                                type="text",
                                id="settings-role",
                                placeholder="NLP Researcher",
                            ),
                        ],
                        row=False,
                    ),
                ]
            ),
            dbc.Form(
                [
                    html.Br(),
                    html.H5("Contact information"),
                    html.Hr(),
                    dbc.FormGroup(
                        [
                            dbc.Label("Email"),
                            dbc.Input(
                                value=current_user.email,
                                type="email",
                                id="settings-email",
                            ),
                        ],
                        row=False,
                    ),
                    dbc.FormGroup(
                        [
                            dbc.Label("Phone"),
                            dbc.Input(
                                value=current_user.phone,
                                type="tel",
                                id="settings-phone",
                            ),
                        ],
                        row=False,
                    ),
                ]
            ),
            html.Br(),
            dbc.Button(
                "Save",
                n_clicks=0,
                id="settings-save-profile",
                disabled=True,
                color="primary",
            ),
        ]

    def get_account_elements(self):
        return [
            dcc.Location(id="settings-url", refresh=True),
            html.H5(
                f"Permissions: {current_user.permissions.name.replace('_', ' + ')}"
            ),
            html.Hr(),
            html.Br(),
            html.H5("Change username"),
            html.Hr(),
            dbc.Button(
                "Change username",
                n_clicks=0,
                id="settings-change-username",
                color="secondary",
            ),
            dcc.ConfirmDialog(
                id="settings-confirm-change-username",
                message="Are you sure you want to change your username? "
                "This could have unintended consequences.",
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader("Change username"),
                    dbc.ModalBody(
                        dbc.Form(
                            [
                                dbc.FormGroup(
                                    [
                                        dbc.Label("Enter new username"),
                                        dbc.Input(
                                            value=current_user.username,
                                            type="text",
                                            id="settings-new-username",
                                        ),
                                        dbc.FormFeedback(
                                            id="settings-new-username-invalid-feedback",
                                            valid=False,
                                        ),
                                    ],
                                    row=False,
                                )
                            ]
                        )
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Save",
                            id="settings-save-new-username",
                            className="ml-auto",
                            disabled=True,
                        )
                    ),
                ],
                id="settings-change-username-modal",
            ),
            html.Br(),
            html.Br(),
            html.Br(),
            html.H5("Delete account"),
            html.Hr(),
            html.P("Permanently delete your account."),
            dbc.Button(
                "Delete account",
                n_clicks=0,
                id="settings-delete-account",
                color="danger",
            ),
            dcc.ConfirmDialog(
                id="settings-confirm-delete-account",
                message="Are you sure you want to delete your account? "
                "This cannot be undone.",
            ),
        ]

    def get_security_elements(self):
        return [
            html.H5("Change password"),
            html.Hr(),
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
                                id="settings-new-pw-invalid-feedback", valid=False
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
            ),
        ]

    def get_users_elements(self):
        return [
            dbc.Form(
                [
                    dbc.FormGroup(
                        [
                            dbc.Label("Select a user to manage their account"),
                            dcc.Dropdown(
                                id="settings-select-user",
                                options=[
                                    {"label": u, "value": u}
                                    for u in UserService().iter_usernames()
                                    if u != current_user.username
                                ],
                            ),
                        ]
                    )
                ]
            ),
            html.Br(),
            html.H5("Set permissions"),
            html.Hr(),
            dbc.Label("Permissions"),
            dbc.Form(
                [
                    dbc.FormGroup(
                        [
                            dcc.Dropdown(
                                id="settings-set-user-permissions",
                                options=[
                                    {
                                        "label": p.name.replace("_", " + "),
                                        "value": p.name,
                                    }
                                    for p in Permissions
                                ],
                                disabled=True,
                            ),
                            dbc.Button(
                                "Save",
                                n_clicks=0,
                                id="settings-save-user-permissions",
                                disabled=True,
                                color="primary",
                            ),
                        ],
                        className="mr-3",
                    )
                ],
                inline=True,
            ),
            html.Br(),
            html.Br(),
            html.H5("Delete account"),
            html.Hr(),
            html.P("Permanently delete their account."),
            dbc.Button(
                "Delete account",
                n_clicks=0,
                id="settings-delete-user-account",
                color="danger",
                disabled=True,
            ),
            dcc.ConfirmDialog(
                id="settings-confirm-delete-user-account",
                message="Are you sure you want to delete their account? "
                "This cannot be undone.",
            ),
        ]

    def get_elements(self):
        is_admin = current_user.permissions == Permissions.ADMIN
        entries = [
            (
                "profile",
                SidebarEntry(
                    "Profile",
                    self.get_profile_elements(),
                    "Personal settings" if is_admin else None,
                ),
            ),
            ("account", SidebarEntry("Account", self.get_account_elements())),
            ("security", SidebarEntry("Security", self.get_security_elements())),
        ]
        if is_admin:
            entries.append(
                (
                    "users",
                    SidebarEntry(
                        "Users", self.get_users_elements(), "Project settings"
                    ),
                )
            )
        return SidebarLayout(
            "Settings", OrderedDict(entries), self.p.active, self.p.to_dict()
        )

    def get_notifications(self):
        return [
            html.Div(id="settings-account-deleted"),
            html.Div(id="settings-user-permissions-updated"),
            html.Div(id="settings-user-account-deleted"),
            dbc.Toast(
                "Username successfully changed. You'll have to sign back in with your new username now.",
                header="Success",
                icon="success",
                duration=4000,
                id="settings-username-changed-success",
                is_open=False,
                dismissable=True,
            ),
            dbc.Toast(
                "Profile successfully updated",
                header="Success",
                icon="success",
                duration=4000,
                id="settings-profile-updated-success",
                is_open=False,
                dismissable=True,
            ),
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
        [Output("settings-save-user-permissions", "disabled")],
        [
            Input("settings-select-user", "value"),
            Input("settings-set-user-permissions", "value"),
        ],
    )
    def enable_save_user_permissions(v1, v2):
        disabled = not v1 or not v2
        return disabled

    @staticmethod
    @Page.callback(
        [Output("settings-user-permissions-updated", "children")],
        [Input("settings-save-user-permissions", "n_clicks")],
        [
            State("settings-select-user", "value"),
            State("settings-set-user-permissions", "value"),
        ],
    )
    def update_user_permissions(n_clicks, username, value):
        if not n_clicks or not username or not value:
            raise PreventUpdate
        permissions = getattr(Permissions, value)
        if UserService().set_permissions(username, permissions):
            return dbc.Toast(
                f"Successfully updated user permissions to {value.replace('_', ' + ')}.",
                header="Success",
                icon="success",
                duration=4000,
                id="settings-update-user-permissions-success",
                is_open=True,
                dismissable=True,
            )
        return dbc.Toast(
            "Failed to update user permissions",
            header="Failed",
            icon="danger",
            duration=4000,
            id="settings-update-user-permissions-fail",
            is_open=True,
            dismissable=True,
        )

    @staticmethod
    @Page.callback(
        [Output("settings-set-user-permissions", "value")],
        [Input("settings-select-user", "value")],
    )
    def update_selected_permissions(value):
        if not value:
            return None
        user = UserService().find(value, check_password=False)
        if not user:
            return None
        return user.permissions.name

    @staticmethod
    @Page.callback(
        [
            Output("settings-set-user-permissions", "disabled"),
            Output("settings-delete-user-account", "disabled"),
        ],
        [Input("settings-select-user", "value")],
    )
    def enable_user_management(value):
        disabled = not value
        return disabled, disabled

    @staticmethod
    @Page.callback(
        [Output("settings-confirm-change-username", "displayed")],
        [Input("settings-change-username", "n_clicks")],
    )
    def display_confirm_change_username(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return True

    @staticmethod
    @Page.callback(
        [Output("settings-confirm-delete-account", "displayed")],
        [Input("settings-delete-account", "n_clicks")],
    )
    def display_confirm_delete_account(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return True

    @staticmethod
    @Page.callback(
        [Output("settings-account-deleted", "children")],
        [Input("settings-confirm-delete-account", "submit_n_clicks")],
    )
    def notify_delete_account(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return dbc.Toast(
            "Your account has been deleted. Sorry to see you go :(",
            header="Account deleted",
            icon="danger",
            duration=4000,
            id="settings-account-deleted-noti",
            is_open=True,
            dismissable=True,
        )

    @staticmethod
    @Page.callback(
        [Output("settings-url", "pathname")],
        [Input("settings-account-deleted", "children")],
    )
    def delete_account(noti):
        if not noti:
            raise PreventUpdate
        time.sleep(1)
        UserService().delete_user(current_user)
        logout_user()
        return "/logout"

    @staticmethod
    @Page.callback(
        [Output("settings-change-username-modal", "is_open")],
        [Input("settings-confirm-change-username", "submit_n_clicks")],
    )
    def open_change_username_modal(n_clicks):
        if not n_clicks:
            return False
        return True

    @staticmethod
    @Page.callback(
        [
            Output("settings-new-username", "valid"),
            Output("settings-new-username", "invalid"),
            Output("settings-new-username-invalid-feedback", "children"),
        ],
        [Input("settings-new-username", "value")],
    )
    def new_username_feedback(value):
        if not value or value == current_user.username:
            return False, False, None
        valid = UserService().find(value, check_password=False) is None
        feedback = "Username already exists" if not valid else None
        return valid, not valid, feedback

    @staticmethod
    @Page.callback(
        [Output("settings-save-new-username", "disabled")],
        [Input("settings-new-username", "valid")],
    )
    def enable_save_new_username(valid):
        if not valid:
            return True
        return False

    @staticmethod
    @Page.callback(
        [Output("settings-username-changed-success", "is_open")],
        [Input("settings-save-new-username", "n_clicks")],
        [State("settings-new-username", "value")],
    )
    def change_username(n_clicks, value):
        if not n_clicks:
            raise PreventUpdate
        UserService().change_username(current_user, value)
        return True

    @staticmethod
    @Page.callback(
        [Output("settings-save-profile", "disabled")],
        [
            Input("settings-fullname", "value"),
            Input("settings-nickname", "value"),
            Input("settings-role", "value"),
            Input("settings-email", "value"),
            Input("settings-phone", "value"),
        ],
    )
    def enable_profile_save_button(fullname, nickname, role, email, phone):
        if fullname != current_user.fullname:
            return False
        if nickname != current_user.nickname:
            return False
        if role != current_user.role:
            return False
        if email != current_user.email:
            return False
        if phone != current_user.phone:
            return False
        return True

    @staticmethod
    @Page.callback(
        [Output("settings-profile-updated-success", "is_open")],
        [Input("settings-save-profile", "n_clicks")],
        [
            State("settings-fullname", "value"),
            State("settings-nickname", "value"),
            State("settings-role", "value"),
            State("settings-email", "value"),
            State("settings-phone", "value"),
        ],
    )
    def save_profile(n_clicks, fullname, nickname, role, email, phone):
        if not n_clicks:
            raise PreventUpdate
        current_user.fullname = fullname
        current_user.nickname = nickname
        current_user.role = role
        current_user.email = email
        current_user.phone = phone
        UserService().update_user(current_user)
        return True

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

    @staticmethod
    @Page.callback(
        [Output("settings-confirm-delete-user-account", "displayed")],
        [Input("settings-delete-user-account", "n_clicks")],
    )
    def display_confirm_delete_user_account(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return True

    @staticmethod
    @Page.callback(
        [
            Output("settings-user-account-deleted", "children"),
            Output("settings-select-user", "options"),
            Output("settings-select-user", "value"),
        ],
        [Input("settings-confirm-delete-user-account", "submit_n_clicks")],
        [State("settings-select-user", "value")],
    )
    def delete_user_account(n_clicks, username):
        if not n_clicks or not username:
            raise PreventUpdate
        UserService().delete_by_username(username)
        return (
            dbc.Toast(
                "User's account successfully deleted",
                header="Account deleted",
                icon="danger",
                duration=4000,
                id="settings-user-account-deleted-noti",
                is_open=True,
                dismissable=True,
            ),
            [
                {"label": u, "value": u}
                for u in UserService().iter_usernames()
                if u != current_user.username
            ],
            None,
        )
