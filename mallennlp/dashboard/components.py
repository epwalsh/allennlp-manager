import urllib.parse
from typing import Any, Dict, NamedTuple, List

import dash_bootstrap_components as dbc
import dash_html_components as html

from mallennlp.exceptions import InvalidPageParametersError


class SidebarEntry(NamedTuple):
    heading: str
    contents: List[Any]


def SidebarItem(heading, location, is_active):
    return dbc.NavItem(dbc.NavLink(heading, href=location, active=is_active))


def Sidebar(
    header: str,
    entries: Dict[str, SidebarEntry],
    active_item: str,
    param_string: str = "",
):
    if len(entries) == 1:
        return [html.H3(header)]
    items = [
        SidebarItem(
            entry.heading, f"?{param_string}active={entry_id}", active_item == entry_id
        )
        for entry_id, entry in entries.items()
    ]
    return [html.H3(header), dbc.Nav(items, className="sidebar-nav")]


def SidebarLayout(
    header: str,
    entries: Dict[str, SidebarEntry],
    active_item: str,
    other_params: Dict[str, Any] = None,
):
    if active_item not in entries:
        raise InvalidPageParametersError("Bad sidebar option")
    if other_params:
        param_string = (
            urllib.parse.urlencode(
                {k: v for k, v in other_params.items() if k != "active"}, doseq=True
            )
            + "&"
        )
    return [
        dbc.Row(
            [
                dbc.Col(Sidebar(header, entries, active_item, param_string), md=3),
                dbc.Col(
                    entries[active_item].contents,
                    md=9,
                    className="dash-padded-element dash-element-no-hover",
                ),
            ]
        )
    ]
