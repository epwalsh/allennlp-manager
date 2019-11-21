import urllib.parse
from typing import Union, Any, Optional, Dict, NamedTuple, List

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from mallennlp.exceptions import InvalidPageParametersError


def element_col(
    children: Any,
    width: Union[str, bool, int, dict] = "auto",
    pad: bool = True,
    hover: bool = False,
    side: str = "left",
    style: Optional[Dict[str, str]] = None,
    md: int = None,
):
    class_names = ["dash-element"]
    if pad:
        class_names.append("dash-padded-element")
    if hover:
        class_names.append("dash-element-hover")
    else:
        class_names.append("dash-element-no-hover")
    if side == "right":
        class_names.append("dash-element-align-right")
    return dbc.Col(
        children, className=" ".join(class_names), width=width, style=style, md=md
    )


def element(
    children: Any,
    width: Union[str, bool, int] = "auto",
    pad: bool = True,
    hover: bool = False,
):
    """
    Create a shadowed-boxed element.

    Parameters
    ----------
    children : ``Any``, required
        A component or list of components.
    width : ``Union[str, bool, int]``, optional (default = 'auto')
        See https://dash-bootstrap-components.opensource.faculty.ai/l/components/layout.
        Set to 'auto' to fit the natural width of children or ``True`` to fit the
        entire page width.
    pad : ``bool``, optional (default = ``True``)
        If True, children will be padded.
    hover : ``bool``, optional (default = ``False``)
        If True, shadowed-border only visible on hover.

    """
    return dbc.Row([element_col(children, width=width, pad=pad, hover=hover)])


def breadcrumb(text: str, link: str):
    return element(
        dcc.Link(
            href=link,
            children=[
                html.I(className="fas fa-chevron-left dash-breadcrumb-left-chevron"),
                text,
            ],
        ),
        pad=False,
        hover=True,
    )


def back_and_next_breadcrumbs(
    back_text: str, back_link: Optional[str], next_text: str, next_link: Optional[str]
):
    back_children: Any
    next_children: Any
    if back_link:
        back_children = dcc.Link(
            href=back_link,
            children=[
                html.I(className="fas fa-chevron-left dash-breadcrumb-left-chevron"),
                back_text,
            ],
        )
    else:
        back_children = [
            html.I(className="fas fa-chevron-left dash-breadcrumb-left-chevron"),
            back_text,
        ]
    if next_link:
        next_children = dcc.Link(
            href=next_link,
            children=[
                next_text,
                html.I(className="fas fa-chevron-right dash-breadcrumb-right-chevron"),
            ],
        )
    else:
        next_children = [
            next_text,
            html.I(className="fas fa-chevron-right dash-breadcrumb-right-chevron"),
        ]
    return dbc.Row(
        [
            element_col(back_children, pad=False, hover=True),
            element_col(next_children, pad=False, hover=True, side="right"),
        ],
        justify="between",
    )


def collapse(title: Any, content: Any, button_id: str, content_id: str) -> html.Div:
    collapse_button = dbc.Button(
        html.I(className="fas fa-chevron-down"),
        color="link",
        outline=True,
        style={"display": "inline-block", "padding-top": "0", "padding-bottom": "0"},
        id=button_id,
    )
    return html.Div(
        [
            html.Span([title, collapse_button]),
            dbc.Collapse(
                dbc.Card(dbc.CardBody(content, style={"padding": "5px"})),
                id=content_id,
                is_open=False,
            ),
        ]
    )


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
