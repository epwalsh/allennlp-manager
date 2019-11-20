from pathlib import Path
import urllib.parse
from typing import Optional, List, Any, Dict, NamedTuple

from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_html_components as html

from mallennlp.controllers.experiment import (
    render_dash_table,
    get_dash_table_data,
    get_all_tags,
    PAGE_SIZE,
    edit_tags_modal,
)
from mallennlp.dashboard.page import Page
from mallennlp.dashboard.components import element
from mallennlp.services.cache import cache
from mallennlp.services.serialization import serializable
from mallennlp.services.experiment import ExperimentService
from mallennlp.services.url_parse import from_url


class UpdateActionsOut(NamedTuple):
    open_disabled: bool = True
    open_href: Optional[str] = None
    edit_tags_modal_disabled: bool = True
    compare_disabled: bool = True
    compare_href: Optional[str] = None


@Page.register("/")
class IndexPage(Page):
    @serializable
    class SessionState:
        selected: Optional[List[Dict[str, Any]]] = None
        """
        Keep track of selected row(s).
        """

    @from_url
    @serializable
    class Params:
        filter_query: str = ""

    def get_elements(self):
        return [
            html.H3("Home"),
            # Dummy divs used to trigger the `render_table_data` callback
            # after other callbacks that modify the data.
            html.Div(id="index-tags-edited-success"),
            html.Div(id="index-database-rebuilt-success"),
            ####################################################################
            # < Main content >
            ####################################################################
            element(
                [
                    ############################################################
                    # < Actions and settings row >
                    ############################################################
                    dbc.Row(
                        [
                            ####################################################
                            # < Actions >
                            ####################################################
                            dbc.Col(
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupAddon(
                                            dbc.Checkbox(
                                                id="experiments-table-select-all"
                                            ),
                                            addon_type="prepend",
                                        ),
                                        dbc.DropdownMenu(
                                            [
                                                dbc.DropdownMenuItem(
                                                    "Open",
                                                    id="experiments-table-open",
                                                    disabled=True,
                                                ),
                                                dbc.DropdownMenuItem(
                                                    "Edit tags",
                                                    id="index-edit-tags-modal-open",
                                                    disabled=True,
                                                ),
                                                dbc.DropdownMenuItem(
                                                    "Compare",
                                                    id="experiments-table-compare",
                                                    disabled=True,
                                                ),
                                                html.Hr(),
                                                dbc.DropdownMenuItem(
                                                    [
                                                        html.I(
                                                            className="fas fa-tools"
                                                        ),
                                                        " Re-build database",
                                                    ],
                                                    id="re-build-database",
                                                ),
                                            ],
                                            label="Actions",
                                            id="experiments-table-actions",
                                        ),
                                    ],
                                    className="mb-3",
                                )
                            ),
                            ####################################################
                            # </ Actions >
                            ####################################################
                            ####################################################
                            # < Settings >
                            ####################################################
                            dbc.Col(
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupAddon(
                                            "Page size", addon_type="prepend"
                                        ),
                                        dbc.Input(
                                            id="index-set-page-size",
                                            type="number",
                                            min=1,
                                            step=1,
                                            value=PAGE_SIZE,
                                        ),
                                    ],
                                    #  className="mb-3",
                                ),
                                className="dash-col-align-right",
                                lg=3,
                                md=4,
                                width=6,
                            ),
                            ####################################################
                            # </ Settings >
                            ####################################################
                        ],
                        justify="between",
                    ),
                    ############################################################
                    # </ Actions and settings row >
                    ############################################################
                    ############################################################
                    # < Edit tags modal pop out >
                    ############################################################
                    edit_tags_modal("index"),
                    ############################################################
                    # </ Edit tags modal pop out >
                    ############################################################
                    ############################################################
                    # < Main table >
                    ############################################################
                    render_dash_table(filter_query=self.p.filter_query),
                    ############################################################
                    # </ Main table >
                    ############################################################
                ],
                width=True,
            ),
            ####################################################################
            # </ Main content >
            ####################################################################
        ]

    def get_notifications(self):
        return [
            dbc.Toast(
                "Tags successfully updated",
                id="index-edit-tags-noti",
                header="Success",
                dismissable=True,
                duration=4000,
                is_open=False,
                icon="success",
            ),
            html.Div(id="database-build-noti-container"),
            dbc.Toast(
                "Database successfully re-built",
                id="database-build-finish-noti",
                header="Success",
                dismissable=True,
                duration=4000,
                is_open=False,
                icon="success",
            ),
        ]

    @staticmethod
    @Page.callback(
        [Output("experiments-table", "page_size")],
        [Input("index-set-page-size", "value")],
    )
    def update_page_size(value):
        if not value:
            raise PreventUpdate
        return value

    @staticmethod
    @Page.callback(
        [Output("experiments-table", "data")],
        [
            Input("experiments-table", "page_current"),
            Input("experiments-table", "page_size"),
            Input("experiments-table", "sort_by"),
            Input("experiments-table", "filter_query"),
            Input("index-tags-edited-success", "children"),
            Input("index-database-rebuilt-success", "children"),
        ],
    )
    def render_table_data(
        page, page_size, sort_by, filter_expression, tags_updated, db_updated
    ):
        if page is None or page_size is None:
            raise PreventUpdate
        return get_dash_table_data(page, page_size, sort_by, filter_expression)

    @staticmethod
    @Page.callback(
        [Output("experiments-table", "selected_rows")],
        [
            Input("experiments-table-select-all", "checked"),
            Input("experiments-table", "data"),
        ],
    )
    def select_all(checked, data):
        if not data:
            raise PreventUpdate
        if not checked:
            return []
        return list(range(len(data)))

    @Page.callback(
        [
            # Open button.
            Output("experiments-table-open", "disabled"),
            Output("experiments-table-open", "href"),
            # Edit tags button.
            Output("index-edit-tags-modal-open", "disabled"),
            # Compare button.
            Output("experiments-table-compare", "disabled"),
            Output("experiments-table-compare", "href"),
        ],
        [
            Input("experiments-table", "data"),
            Input("experiments-table", "selected_rows"),
        ],
        mutating=True,
    )
    def update_actions(self, data, selected):
        if not data or not selected:
            return UpdateActionsOut()
        self.s.selected = [data[i] for i in selected if i < len(data)]
        if len(self.s.selected) > 1:
            return UpdateActionsOut(
                compare_disabled=False,
                compare_href="/compare?"
                + urllib.parse.urlencode(
                    {"paths": [r["path"] for r in self.s.selected]}, doseq=True
                ),
            )
        return UpdateActionsOut(
            open_disabled=False,
            open_href="/experiment?"
            + urllib.parse.urlencode({"path": self.s.selected[0]["path"]}),
            edit_tags_modal_disabled=False,
        )

    @Page.callback(
        [
            Output("index-edit-tags-modal", "is_open"),
            Output("index-edit-tags-dropdown", "value"),
        ],
        [
            Input("index-edit-tags-modal-open", "n_clicks"),
            Input("index-edit-tags-modal-close", "n_clicks"),
        ],
        [State("index-edit-tags-modal", "is_open")],
        mutating=False,
    )
    def toggle_modal(self, n1, n2, is_open):
        tags: Optional[List[str]] = None
        if n1 or n2:
            will_open = not is_open and self.s.selected
            if will_open:
                tags = [t for t in self.s.selected[0]["tags"].split(" ") if t]
            return will_open, tags
        return is_open, tags

    @staticmethod
    @Page.callback(
        [Output("index-edit-tags-dropdown", "options")],
        [Input("index-edit-tags-dropdown", "search_value")],
        [State("index-edit-tags-dropdown", "value")],
    )
    def update_tag_options(search, value):
        if not search:
            raise PreventUpdate
        options = {t for t in get_all_tags() if t.startswith(search)}
        options.add(search)
        for v in value or []:
            options.add(v)
        return [{"label": t, "value": t} for t in options]

    @Page.callback(
        [
            Output("index-edit-tags-noti", "is_open"),
            Output("index-tags-edited-success", "children"),
        ],
        [Input("index-edit-tags-save", "n_clicks")],
        [State("index-edit-tags-dropdown", "value")],
        mutating=True,
    )
    def save_tags(self, n_clicks, tags):
        if not n_clicks or not self.s.selected or not len(self.s.selected) == 1:
            raise PreventUpdate
        es = ExperimentService(Path(self.s.selected[0]["path"]))
        es.set_tags(tags)
        self.s.selected[0]["tags"] = " ".join(tags)
        all_tags = get_all_tags()
        if any(tag not in all_tags for tag in tags):
            # Need to clear the memoized cache for `get_all_tags` now.
            cache.delete_memoized(get_all_tags)
        return True, None

    @staticmethod
    @Page.callback(
        [Output("re-build-database", "disabled")],
        [Input("database-build-noti", "is_open")],
    )
    def update_build_button(build_in_progress):
        return build_in_progress

    @staticmethod
    @Page.callback(
        [Output("database-build-noti-container", "children")],
        [Input("re-build-database", "n_clicks")],
    )
    def notify_re_build_database(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return dbc.Toast(
            [
                dbc.Spinner(color="info", size="sm", style={"margin-right": "5px"}),
                "Re-building database",
            ],
            id="database-build-noti",
            header="In progress",
            is_open=True,
            icon="info",
        )

    @staticmethod
    @Page.callback(
        [
            Output("database-build-noti", "is_open"),
            Output("database-build-finish-noti", "is_open"),
            Output("index-database-rebuilt-success", "children"),
        ],
        [Input("re-build-database", "n_clicks")],
    )
    def re_build_database(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        # TODO: remove the sleep.
        import time

        time.sleep(1)

        # Remove any deleted experiments, track new experiments added.
        ExperimentService.init_db_table()
        # Clear the memoized cache for `get_all_tags` now.
        cache.delete_memoized(get_all_tags)
        return False, True, None
