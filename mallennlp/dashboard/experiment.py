from collections import OrderedDict
from pathlib import Path
from typing import Optional, List

import attr
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import mallennlp.controllers.experiment as ec
from mallennlp.dashboard.components import SidebarEntry, SidebarLayout
from mallennlp.dashboard.page import Page
from mallennlp.domain.experiment import Status
from mallennlp.exceptions import InvalidPageParametersError
from mallennlp.services.cache import cache
from mallennlp.services.experiment import ExperimentService
from mallennlp.services.serialization import serializable
from mallennlp.services.url_parse import from_url


@Page.register("/experiment")
class ExperimentPage(Page):
    @from_url
    @serializable
    class Params:
        path: str = attr.ib()
        active: str = "overview"

        @path.validator
        def check_path_valid(self, attribute, value):
            try:
                path = ExperimentService.get_canonical_path(Path(value))
                if not path.exists():
                    raise InvalidPageParametersError("Directory does not exist.")
                if path.is_dir() and not ExperimentService.is_experiment(path):
                    raise InvalidPageParametersError("Directory is not an experiment.")
                if path.is_file():
                    raise InvalidPageParametersError(
                        "Path is a file, not an experiment directory."
                    )
            except ValueError:
                raise InvalidPageParametersError("Directory outside of project.")
            return str(path)

    def __init__(self, state, params):
        super().__init__(state, params)
        self.path = ExperimentService.get_canonical_path(Path(self.p.path))
        self.es = ExperimentService(self.path)

    def get_overview_elements(self):
        status = ec.get_status(self.es)
        elements = [
            html.H5(
                [
                    f"{str(self.path)}",
                    html.Span(
                        id="experiment-status-badge",
                        children=ec.get_status_badge(status),
                    ),
                ]
            ),
            html.Div(id="experiment-tags", children=ec.display_tags(self.es)),
            ec.edit_tags_modal("experiment"),
            html.Hr(),
            html.Div(id="experiment-metrics", children=ec.display_metrics(self.es)),
        ]
        if status not in (Status.FINISHED, Status.FAILED):
            # If experiment is not finished or failed, then we should periodically update.
            elements.append(
                dcc.Interval(id="experiment-update-interval", interval=1000 * 30)
            )
        return elements

    def get_elements(self):
        # Update database entry.
        self.es.update_db_entry()
        # Create sidebar entries.
        entries = OrderedDict(
            [("overview", SidebarEntry("Overview", self.get_overview_elements()))]
        )
        return SidebarLayout("Experiment", entries, self.p.active, self.p.to_dict())

    def get_notifications(self):
        return [
            dbc.Toast(
                "Tags successfully updated",
                id="experiment-edit-tags-noti",
                header="Success",
                dismissable=True,
                duration=4000,
                is_open=False,
                icon="success",
            )
        ]

    @Page.callback(
        [Output("experiment-status-badge", "children")],
        [Input("experiment-update-interval", "n_intervals")],
        mutating=False,
    )
    def update_status_badge(self, _):
        # Update database entry.
        self.es.update_db_entry()
        status = ec.get_status(self.es)
        return ec.get_status_badge(status)

    @Page.callback(
        [Output("experiment-metrics", "children")],
        [Input("experiment-update-interval", "n_intervals")],
        mutating=False,
    )
    def update_metrics(self, _):
        return ec.display_metrics(self.es)

    @Page.callback(
        [Output("experiment-tags", "children")],
        [Input(f"experiment-tag-{i}", "n_clicks") for i in range(ec.MAX_TAG_BADGES)]
        + [Input("experiment-edit-tags-noti", "is_open")],
        [State(f"experiment-tag-{i}", "key") for i in range(ec.MAX_TAG_BADGES)],
        mutating=False,
    )
    def update_tags(self, *args):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id.startswith("experiment-tag-"):
            # Try deleting tag.
            current_tags = self.es.get_tags()
            tag = ctx.states[f"{button_id}.key"]
            if tag in current_tags:
                self.es.set_tags([t for t in current_tags if t != tag])
                # Need to clear the memoized cache for `get_all_tags` now.
                cache.delete_memoized(ec.get_all_tags)
        return ec.display_tags(self.es)

    @Page.callback(
        [
            Output("experiment-edit-tags-modal", "is_open"),
            Output("experiment-edit-tags-dropdown", "value"),
        ],
        [
            Input("experiment-edit-tags-modal-open", "n_clicks"),
            Input("experiment-edit-tags-modal-close", "n_clicks"),
        ],
        [State("experiment-edit-tags-modal", "is_open")],
        mutating=False,
    )
    def toggle_modal(self, n1, n2, is_open):
        tags: Optional[List[str]] = None
        if n1 or n2:
            will_open = not is_open
            if will_open and self.es:
                tags = self.es.get_tags()
            return will_open, tags
        return is_open, tags

    @staticmethod
    @Page.callback(
        [Output("experiment-edit-tags-dropdown", "options")],
        [Input("experiment-edit-tags-dropdown", "search_value")],
        [State("experiment-edit-tags-dropdown", "value")],
    )
    def update_tag_options(search, value):
        if not search:
            raise PreventUpdate
        options = {t for t in ec.get_all_tags() if t.startswith(search)}
        options.add(search)
        for v in value or []:
            options.add(v)
        return [{"label": t, "value": t} for t in options]

    @Page.callback(
        [Output("experiment-edit-tags-noti", "is_open")],
        [Input("experiment-edit-tags-save", "n_clicks")],
        [State("experiment-edit-tags-dropdown", "value")],
        mutating=False,
    )
    def save_tags(self, n_clicks, tags):
        if not n_clicks:
            raise PreventUpdate
        self.es.set_tags(tags)
        all_tags = ec.get_all_tags()
        if any(tag not in all_tags for tag in tags):
            # Need to clear the memoized cache for `get_all_tags` now.
            cache.delete_memoized(ec.get_all_tags)
        return True
