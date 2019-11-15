from pathlib import Path
import urllib.parse
from typing import Optional, List, Any, Dict, NamedTuple

from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from mallennlp.controllers.experiment import (
    render_dash_table,
    get_dash_table_data,
    get_all_tags,
)
from mallennlp.dashboard.page import Page
from mallennlp.dashboard.components import element
from mallennlp.services.cache import cache
from mallennlp.services.serialization import serializable
from mallennlp.services.experiment import ExperimentService


@Page.register("/")
class IndexPage(Page):
    @serializable
    class SessionState:
        selected: Optional[List[Dict[str, Any]]] = None
        """
        Keep track of selected row(s).
        """

    def get_elements(self):
        return [
            html.H3("Home"),
            element(
                [
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon(
                                dbc.Checkbox(id="experiments-table-select-all"),
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
                                    html.Hr(),
                                    dbc.DropdownMenuItem(
                                        "Compare",
                                        id="experiments-table-compare",
                                        disabled=True,
                                    ),
                                ],
                                label="Actions",
                                id="experiments-table-actions",
                            ),
                        ],
                        className="mb-3",
                    ),
                    dbc.Modal(
                        [
                            dbc.ModalHeader("Edit tags"),
                            dbc.ModalBody(
                                [
                                    dcc.Dropdown(
                                        id="index-edit-tags-dropdown",
                                        multi=True,
                                        options=[
                                            {"label": t, "value": t}
                                            for t in get_all_tags()
                                        ],
                                    )
                                ]
                            ),
                            dbc.ModalFooter(
                                [
                                    dbc.Button(
                                        "Save", id="index-edit-tags-save", color="info"
                                    ),
                                    dbc.Button(
                                        "Close",
                                        id="index-edit-tags-modal-close",
                                        className="ml-auto",
                                    ),
                                ]
                            ),
                        ],
                        id="index-edit-tags-modal",
                    ),
                    render_dash_table(),
                    html.Div(id="index-edit-tags-status"),
                ],
                width=True,
            ),
        ]

    @Page.callback(
        [Output("experiments-table", "data")],
        [
            Input("experiments-table", "page_current"),
            Input("experiments-table", "page_size"),
            Input("experiments-table", "sort_by"),
            Input("experiments-table", "filter_query"),
            Input("index-edit-tags-status", "children"),
        ],
    )
    def render_table_data(self, page, page_size, sort_by, filter_expression, status):
        if page is None or page_size is None:
            raise PreventUpdate
        return get_dash_table_data(page, page_size, sort_by, filter_expression)

    @Page.callback(
        [Output("experiments-table", "selected_rows")],
        [Input("experiments-table-select-all", "checked")],
        [State("experiments-table", "page_size")],
    )
    def select_all(self, checked, page_size):
        if not page_size:
            raise PreventUpdate
        if not checked:
            return []
        return list(range(page_size))

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
    )
    def update_actions(self, data, selected):
        class Output(NamedTuple):
            open_disabled: bool = True
            open_href: Optional[str] = None
            edit_tags_modal_disabled: bool = True
            compare_disabled: bool = True
            compare_href: Optional[str] = None

        if not data or not selected:
            return Output()
        self.s.selected = [data[i] for i in selected]
        if len(self.s.selected) > 1:
            return Output(
                compare_disabled=False,
                compare_href="/compare?"
                + urllib.parse.urlencode(
                    {"path": [r["path"] for r in self.s.selected]}, doseq=True
                ),
            )
        return Output(
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
    )
    def toggle_modal(self, n1, n2, is_open):
        tags: Optional[List[str]] = None
        if n1 or n2:
            will_open = not is_open and self.s.selected
            if will_open:
                tags = [t for t in self.s.selected[0]["tags"].split(" ") if t]
            return will_open, tags
        return is_open, tags

    @Page.callback(
        [Output("index-edit-tags-dropdown", "options")],
        [Input("index-edit-tags-dropdown", "search_value")],
        [State("index-edit-tags-dropdown", "value")],
    )
    def update_tag_options(self, search, value):
        if not search:
            raise PreventUpdate
        options = {t for t in get_all_tags() if t.startswith(search)}
        options.add(search)
        for v in value or []:
            options.add(v)
        return [{"label": t, "value": t} for t in options]

    @Page.callback(
        [Output("index-edit-tags-status", "children")],
        [Input("index-edit-tags-save", "n_clicks")],
        [State("index-edit-tags-dropdown", "value")],
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
        return dbc.Toast(
            "Tags successfully updated",
            id="index-edit-tags-status-toast",
            header="Success",
            dismissable=True,
            duration=4000,
            icon="success",
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        )
