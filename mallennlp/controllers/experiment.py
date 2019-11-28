from collections import OrderedDict
import urllib.parse
from pathlib import Path
from typing import Any, List, Dict, Tuple, Set

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from mallennlp.domain.experiment import Status
from mallennlp.services.cache import cache
from mallennlp.services.db import Tables, get_db_from_app
from mallennlp.services.experiment import ExperimentService


PAGE_SIZE = 10
MAX_TAG_BADGES = 10


def parse_filters(filter_expression) -> Tuple[str, List[str]]:
    filters: List[str] = []
    filter_args: List[str] = []
    for filter_part in filter_expression.split(" && "):
        # Filter part looks like `{column_id} contains input_value`
        name_part, value = filter_part.split(" contains ", 1)
        col_name = name_part[name_part.find("{") + 1 : name_part.rfind("}")]
        value = value.strip()
        if not value:
            continue
        if col_name == "path":
            # Interpret filter for 'path' column as a GLOB.
            filters.append("path GLOB ?")
            filter_args.append(value)
        elif col_name == "tags":
            # Interpret filter for 'tags' column as a 'HasAllTags' query.
            tags = [t for t in value.split(" ") if t]
            filters.append(f"HasAllTags(tags, {', '.join('?' for _ in tags)})")
            filter_args.extend(tags)
        elif col_name == "finished":
            if value.lower() in ("yes", "finished", "done", "success"):
                filters.append("finished = 1")
            elif value.lower() == "no":
                filters.append("finished = 0")
    return " AND ".join(filters), filter_args


def get_dash_table_data(
    page: int = 0,
    page_size: int = PAGE_SIZE,
    sort_by: List[Dict[str, Any]] = None,
    filter_expression: str = None,
):
    db = get_db_from_app()
    offset = page * page_size
    if sort_by:
        sort_field = sort_by[0]["column_id"]
        sort_direction = "ASC" if sort_by[0]["direction"] == "asc" else "DESC"
    else:
        sort_field = "path"
        sort_direction = "ASC"
    if filter_expression and " contains " in filter_expression:
        where_clause, args = parse_filters(filter_expression)
        cursor = db.execute(
            f"SELECT * "
            f"FROM {Tables.EXPERIMENTS.value} "
            f"WHERE {where_clause} "
            f"ORDER BY {sort_field} {sort_direction} "
            f"LIMIT {offset}, {page_size}",
            args,
        )
    else:
        cursor = db.execute(
            f"SELECT * "
            f"FROM {Tables.EXPERIMENTS.value} "
            f"ORDER BY {sort_field} {sort_direction} "
            f"LIMIT {offset}, {page_size}"
        )
    return [
        {
            "path": row["path"],
            "tags": row["tags"],
            "finished": "Yes" if row["finished"] else "No",
        }
        for row in cursor
    ]


def render_dash_table(filter_query: str = None):
    filter_query = filter_query or "{path} contains *"
    return dash_table.DataTable(
        id="experiments-table",
        #  data=get_dash_table_data(filter_expression=filter_query),
        columns=[
            {"id": "path", "name": "Path"},
            {"id": "tags", "name": "Tags"},
            {"id": "finished", "name": "Finished"},
        ],
        #  style_as_list_view=True,
        style_data={"textAlign": "left"},
        style_header={"textAlign": "left", "fontWeight": "bold"},
        style_filter={"textAlign": "left"},
        style_cell={"padding": "10px"},
        style_cell_conditional=[
            #  {"if": {"column_id": "path"}, "textAlign": "left"},
            # Overflow tags into multiple lines, splitting on whitespace.
            {
                "if": {"column_id": "tags"},
                "whiteSpace": "normal",
                "height": "auto",
                "minWidth": "0px",
                "maxWidth": "200px",
            }
        ],
        style_data_conditional=[
            {
                "if": {"filter_query": "{finished} eq 'Yes'", "column_id": "finished"},
                "backgroundColor": "#a2ed95",
            }
        ],
        style_table={"overflowX": "scroll"},
        #  page_current=0,
        #  page_size=PAGE_SIZE,
        page_action="custom",
        sort_action="custom",
        sort_mode="single",
        #  sort_by=[],
        filter_action="custom",
        filter_query=filter_query,
        row_selectable="multi",
        persistence=True,
        persistence_type="memory",
        #  persisted_props=["selected", "page_size", "filter_query"],
    )


@cache.memoize(timeout=60 * 5)
def get_all_tags() -> Set[str]:
    db = get_db_from_app()
    cursor = db.execute(f"SELECT tags FROM {Tables.EXPERIMENTS.value}")
    return set(t for r in cursor for t in r["tags"].split(" ") if t)


@cache.memoize(timeout=30)
def get_status(es: ExperimentService) -> Status:
    return es.get_status()


def get_status_badge(status: Status):
    if status == Status.FINISHED:
        status_badge_color = "success"
    elif status == Status.FAILED:
        status_badge_color = "danger"
    elif status == Status.IN_PROGRESS:
        status_badge_color = "primary"
    else:
        status_badge_color = "secondary"
    return dbc.Badge(
        status.value, color=status_badge_color, className="experiment-status-badge"
    )


def get_tag_filter_query(t: str):
    return urllib.parse.urlencode({"filter_query": "{tags} contains %s" % t})


def edit_tags_modal(id_prefix: str):
    return dbc.Modal(
        [
            dbc.ModalHeader("Edit tags"),
            dbc.ModalBody(
                [
                    dcc.Dropdown(
                        id=f"{id_prefix}-edit-tags-dropdown",
                        multi=True,
                        options=[{"label": t, "value": t} for t in get_all_tags()],
                    )
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button("Save", id=f"{id_prefix}-edit-tags-save", color="info"),
                    dbc.Button(
                        "Close",
                        id=f"{id_prefix}-edit-tags-modal-close",
                        className="ml-auto",
                    ),
                ]
            ),
        ],
        id=f"{id_prefix}-edit-tags-modal",
    )


def display_tags(es: ExperimentService):
    tags = es.get_tags()
    tag_badges = [
        dbc.Badge(
            [t, html.I(className="fas fa-times-circle", style={"margin-left": "5px"})],
            id=f"experiment-tag-{i}",
            key=t,
            color="info",
            className="mr-1",
            pill=True,
            href="#",
        )
        for i, t in enumerate(tags[:MAX_TAG_BADGES])
    ]
    tooltips = [
        dbc.Tooltip(f"""Remove "{t}" tag""", target=f"experiment-tag-{i}")
        for i, t in enumerate(tags[:MAX_TAG_BADGES])
    ]
    for i in range(len(tags), MAX_TAG_BADGES):
        tag_badges.append(
            dbc.Badge("", id=f"experiment-tag-{i}", href="#", style={"display": "none"})
        )
    if len(tags) > MAX_TAG_BADGES:
        tag_badges.append(
            dbc.Badge(
                html.I(className="fas fa-ellipsis-h"),
                id="experiment-edit-tags-modal-open",
                color="info",
                className="mr-1",
                pill=True,
                href="#",
            )
        )
        tooltips.append(
            dbc.Tooltip(
                "See all tags or edit", target="experiment-edit-tags-modal-open"
            )
        )
    else:
        tag_badges.append(
            dbc.Badge(
                html.I(className="fas fa-edit", style={"margin-left": "3px"}),
                id="experiment-edit-tags-modal-open",
                color="info",
                className="mr-1",
                pill=True,
                href="#",
            )
        )
        tooltips.append(
            dbc.Tooltip("Edit tags", target="experiment-edit-tags-modal-open")
        )
    return [html.Span(tag_badges), html.Div(children=tooltips)]


METRIC_GENERAL_DISPLAY_FIELDS = OrderedDict(
    training_epochs="**Epochs:** `%d`", training_duration="**Training duration:** `%s`"
)

METRIC_EPOCH_DISPLAY_FIELDS = OrderedDict(
    best_epoch="**Best epoch:** `%d`",
    training_loss="**Training loss:** `%f`",
    best_validation_loss="**Validation loss:** `%f`",
)


def display_metrics(es: ExperimentService):
    metrics = es.get_metrics()
    if metrics is None:
        return dcc.Markdown("**No metrics to display**")
    fields: List[str] = []
    for field_name, formatter in METRIC_GENERAL_DISPLAY_FIELDS.items():
        field_value = metrics.get(field_name)
        if field_value is not None:
            fields.append(formatter % field_value)
    fields.append("---")
    for field_name, formatter in METRIC_EPOCH_DISPLAY_FIELDS.items():
        field_value = metrics.get(field_name)
        if field_value is not None:
            fields.append(formatter % field_value)
    for other_field_name in metrics:
        if (
            other_field_name in METRIC_GENERAL_DISPLAY_FIELDS
            or other_field_name in METRIC_EPOCH_DISPLAY_FIELDS
        ):
            continue
        if other_field_name.startswith("best_validation_"):
            field_value = metrics[other_field_name]
            fields.append(
                f"**Validation {other_field_name[16:].replace('_', ' ')}:** `{field_value}`"
            )
    return dcc.Markdown("\n\n".join(fields))


def get_path_breadcrumbs(path: Path):
    parts: List[Any] = [
        dcc.Link(href="/", children=html.I(className="fas fa-home")),
        html.I("/", className="path-divider"),
    ]
    base_path = ""
    for part in path.parts[:-1]:
        base_path = base_path + part + "/"
        parts.extend(
            [
                dcc.Link(
                    href="/?"
                    + urllib.parse.urlencode(
                        {"filter_query": "{path} contains " + base_path + "*"}
                    ),
                    children=part,
                ),
                html.I("/", className="path-divider"),
            ]
        )
    parts.extend([path.parts[-1], html.I("/", className="path-divider")])
    return parts
