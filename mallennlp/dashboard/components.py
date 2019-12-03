from typing import Any, Dict, NamedTuple, List, Optional, Union, Callable

import dash_bootstrap_components as dbc
import dash_html_components as html

from mallennlp.exceptions import InvalidPageParametersError
from mallennlp.services.serde import to_url


class SidebarEntry(NamedTuple):
    heading: str
    contents: Union[List[Any], Callable[[], List[Any]]]
    section_heading: Optional[str] = None
    className: str = "dash-padded-element dash-element-no-hover"


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
    other_params: Optional[Any] = None,
):
    if active_item not in entries:
        raise InvalidPageParametersError("Bad sidebar option")
    if other_params:
        param_string = to_url(
            other_params, filter=lambda a, v: a.name != "active" and v is not None
        )
        if param_string:
            param_string = param_string + "&"
    active = entries[active_item]
    contents = active.contents() if callable(active.contents) else active.contents
    return [
        dbc.Row(
            [
                dbc.Col(Sidebar(header, entries, active_item, param_string), md=3),
                dbc.Col(
                    contents,
                    md=9,
                    className=active.className,
                    id=f"__{header}-{active_item}-sidebar-entry-contents",
                ),
            ]
        )
    ]
