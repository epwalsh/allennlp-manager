import urllib.parse
from typing import Any, Dict, NamedTuple, List, Optional

import dash_bootstrap_components as dbc
import dash_html_components as html

from mallennlp.exceptions import InvalidPageParametersError


class SidebarEntry(NamedTuple):
    heading: str
    contents: List[Any]
    section_heading: Optional[str] = None


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
    items: List[Any] = []
    for entry_id, entry in entries.items():
        if entry.section_heading is not None:
            items.append(
                html.H6(entry.section_heading, className="sidebar-nav-section-heading")
            )
        items.append(
            SidebarItem(
                entry.heading,
                f"?{param_string}active={entry_id}",
                active_item == entry_id,
            )
        )
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
        param_string = urllib.parse.urlencode(
            {k: v for k, v in other_params.items() if k != "active"}, doseq=True
        )
        if param_string:
            param_string = param_string + "&"
    return [
        dbc.Row(
            [
                dbc.Col(Sidebar(header, entries, active_item, param_string), md=3),
                dbc.Col(
                    entries[active_item].contents,
                    md=9,
                    className="dash-padded-element dash-element-no-hover",
                    id=f"__{header}-{active_item}-sidebar-entry-contents",
                ),
            ]
        )
    ]
