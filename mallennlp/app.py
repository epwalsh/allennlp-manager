import inspect
import logging

from allennlp.common.util import import_submodules
from allennlp.common.checks import ConfigurationError
from dash import Dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask, redirect
from flask_login import LoginManager, login_required, logout_user, current_user

from mallennlp.dashboard.callbacks import register_callbacks, store_callback
from mallennlp.dashboard.page import Page
from mallennlp.domain.user import AnonymousUser
from mallennlp.exceptions import InvalidPageParametersError
from mallennlp.services import db, cache
from mallennlp.services.config import Config
from mallennlp.services.user import UserService


def init_dash(flask_app: Flask, config: Config):
    logger = flask_app.logger
    dash = Dash(
        __name__,
        server=flask_app,
        routes_pathname_prefix="/",
        external_stylesheets=[
            #  dbc.themes.BOOTSTRAP,
            #  "https://use.fontawesome.com/releases/v5.8.1/css/all.css"
        ],
        meta_tags=[
            {"charset": "utf-8"},
            {
                "name": "viewport",
                "content": "width=device-width, initial-scale=1, shrink-to-fit=no",
            },
        ],
    )
    dash.config["suppress_callback_exceptions"] = True
    dash.title = config.project.display_name or config.project.name
    dash.layout = html.Div(
        children=[
            # Represents the URL bar, doesn't render anything.
            dcc.Location(id="url", refresh=False),
            dbc.NavbarSimple(
                id="navbar-content",
                brand="AllenNLP Manager",
                brand_href="/",
                sticky="top",
                color="#162328",
                dark=True,
            ),
            dcc.Store(id="current-path"),
            dbc.Container(
                id="notifications",
                style={"position": "fixed", "top": 66, "right": 10, "width": 350},
                children=[
                    html.Div(id="page-loading-error"),
                    html.Div(id="page-notifications"),
                    html.Div(id="page-callback-errors"),
                ],
            ),
            dbc.Container(id="page-content"),
        ]
    )

    # Import all dashboard pages so that they get registered.
    import_submodules("mallennlp.dashboard")
    for module in config.server.imports or []:
        logger.info("Importing additional module %s", module)
        import_submodules(module)

    additional_navlinks = []
    for page_name in Page.list_available():
        PageClass = Page.by_name(page_name)
        if PageClass.navlink_name is not None:
            additional_navlinks.append(
                dbc.DropdownMenuItem(dcc.Link(PageClass.navlink_name, href=page_name))
            )

    Page.logger = logger

    # Define callback to render navbar.
    @dash.callback(Output("navbar-content", "children"), [Input("url", "pathname")])
    def render_navbar(pathname):
        source_link = dbc.NavItem(
            dbc.NavLink(
                [html.I(className="fab fa-github"), " Source"],
                href="https://github.com/epwalsh/allennlp-manager",
            )
        )
        if current_user.is_authenticated:
            menu_items = [
                dbc.DropdownMenuItem(
                    ["Signed in as ", html.Strong(current_user.username)], disabled=True
                ),
                html.Hr(),
                dbc.DropdownMenuItem(dcc.Link("Home", href="/")),
                dbc.DropdownMenuItem(dcc.Link("System Info", href="/sys-info")),
            ]
            if additional_navlinks:
                menu_items.append(html.Hr())
                menu_items.extend(additional_navlinks)
            menu_items.extend(
                [
                    html.Hr(),
                    dbc.DropdownMenuItem(
                        dcc.Link("Logout", href="/logout", refresh=True)
                    ),
                ]
            )
            return [
                source_link,
                dbc.DropdownMenu(
                    nav=True, in_navbar=True, label="Menu", children=menu_items
                ),
            ]
        return [
            source_link,
            dbc.NavItem(dbc.NavLink("Sign in", href="/login", external_link=True)),
        ]

    # Define callback to render pages. Takes the URL path and get the corresponding
    # page.
    @dash.callback(
        [
            Output("page-content", "children"),
            Output("page-callback-errors", "children"),
            Output("page-notifications", "children"),
            Output("page-loading-error", "children"),
            Output("current-path", "data"),
        ],
        [Input("url", "pathname"), Input("url", "search")],
        [State("current-path", "data")],
    )
    def render_page(pathname: str, param_string: str, current_path_data):
        logger.debug("Attempting to render page %s", pathname)
        if pathname is None:
            raise PreventUpdate
        if pathname != "/" and pathname.endswith("/") or pathname.endswith("#"):
            pathname = pathname[:-1]
        if current_path_data:
            # If nothing in the path / param_string has changed, don't actually do anything.
            # NOTE: this is kind of a hack, since sometimes we have buttons w/ href='#',
            # and we don't want to actually re-render the pages content when clicked.
            if (
                current_path_data["pathname"] == pathname
                and current_path_data["param_string"] == param_string
            ):
                raise PreventUpdate
        updated_data = {"pathname": pathname, "param_string": param_string}
        try:
            PageClass = Page.by_name(pathname)
            if PageClass.requires_login and not current_user.is_authenticated:
                PageClass = Page.by_name("/login")
                params = PageClass.Params(
                    next_pathname=pathname, next_params=param_string
                )
                return PageClass.from_params(params).render() + (None, updated_data)

            params = PageClass.Params.from_url(param_string)
            return PageClass.from_params(params).render() + (None, updated_data)
        except ConfigurationError:
            return (
                [],
                [],
                dbc.Toast(f"Page {pathname} not found", header="404", icon="danger"),
                updated_data,
            )
        except InvalidPageParametersError as e:
            return (
                [],
                [],
                dbc.Toast(str(e), header="Bad page parameters", icon="danger"),
                updated_data,
            )
        except Exception as e:
            logger.exception(e)
            return (
                [],
                [],
                dbc.Toast(str(e), header=e.__class__.__name__, icon="danger"),
                updated_data,
            )

    # Now we loop through all registered pages and register their callbacks
    # with the dashboard application.
    for page_name in Page.list_available():
        PageClass = Page.by_name(page_name)
        PageClass.route = page_name
        if getattr(PageClass, "logger", None) is None:
            PageClass.logger = logger
        PageClass._store_name = f"page-{page_name}-store"
        PageClass._callback_stores = []
        PageClass._callback_error_divs = []
        for _, method in filter(
            lambda x: callable(x[1]), inspect.getmembers(PageClass)
        ):
            if not getattr(method, "is_callback", False):
                continue
            register_callbacks(dash, PageClass, method)

        if PageClass._callback_stores:
            dash.callback(
                Output(PageClass._store_name, "data"),
                [Input(s, "modified_timestamp") for s in PageClass._callback_stores],
                [State(s, "data") for s in PageClass._callback_stores],
            )(store_callback)

    return dash


def create_app(config: Config):
    app = Flask(__name__, instance_path=config.server.instance_path)
    app.config.from_object(config.server)

    loglevel = getattr(logging, config.project.loglevel.upper())
    app.logger.setLevel(loglevel)

    db.init_app(app)
    cache.init_app(app, config)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "/login"
    login_manager.anonymous_user = AnonymousUser
    login_manager.session_protection = "strong"

    @login_manager.user_loader
    def load_user(userid: str):
        return UserService().get(userid)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect("/login")

    init_dash(app, config)

    return app


if __name__ == "__main__":
    config = Config.from_toml()
    app = create_app(config)
    app.run(debug=True, host="0.0.0.0")
