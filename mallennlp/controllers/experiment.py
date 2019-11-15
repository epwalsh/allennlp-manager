from typing import Any, List, Dict, Tuple, Set

import dash_table

from mallennlp.services.cache import cache
from mallennlp.services.db import Tables, get_db_from_app


PAGE_SIZE = 2


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
    if filter_expression:
        where_clause, args = parse_filters(filter_expression)
        cursor = db.execute(
            f"SELECT * "
            f"FROM {Tables.EXPERIMENTS.value} "
            f"WHERE {where_clause} "
            f"ORDER BY {sort_field} {sort_direction} "
            f"LIMIT {offset}, {PAGE_SIZE}",
            args,
        )
    else:
        cursor = db.execute(
            f"SELECT * "
            f"FROM {Tables.EXPERIMENTS.value} "
            f"ORDER BY {sort_field} {sort_direction} "
            f"LIMIT {offset}, {PAGE_SIZE}"
        )
    return [{"path": row["path"], "tags": row["tags"]} for row in cursor]


def render_dash_table():
    return dash_table.DataTable(
        id="experiments-table",
        data=get_dash_table_data(),
        columns=[{"id": "path", "name": "Path"}, {"id": "tags", "name": "Tags"}],
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
        style_table={"overflowX": "scroll"},
        page_current=0,
        page_size=PAGE_SIZE,
        page_action="custom",
        sort_action="custom",
        sort_mode="single",
        sort_by=[],
        filter_action="custom",
        filter_query="",
        row_selectable="multi",
    )


@cache.memoize(timeout=60 * 5)
def get_all_tags() -> Set[str]:
    db = get_db_from_app()
    cursor = db.execute(f"SELECT tags FROM {Tables.EXPERIMENTS.value}")
    return set(t for r in cursor for t in r["tags"].split(" ") if t)
