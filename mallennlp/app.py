import inspect
import logging
from pathlib import Path
import urllib.parse as urlparse
from typing import List

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

from mallennlp.dashboard.page import Page
from mallennlp.domain.user import AnonymousUser
from mallennlp.services import db
from mallennlp.services.config import Config
from mallennlp.services.user import UserService


def init_dash(flask_app: Flask, config: Config):
    logger = flask_app.logger
    dash = Dash(
        __name__,
        server=flask_app,
        routes_pathname_prefix="/",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://use.fontawesome.com/releases/v5.8.1/css/all.css",
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
        Output("page-content", "children"),
        [Input("url", "pathname"), Input("url", "search")],
    )
    def render_page(pathname: str, param_string: str) -> html.Div:
        if pathname is None:
            raise PreventUpdate
        params = urlparse.parse_qs(urlparse.urlparse(param_string).query)
        try:
            PageClass = Page.by_name(pathname)
            if PageClass.requires_login and not current_user.is_authenticated:
                PageClass = Page.by_name("/login")
                params = {"next_pathname": [pathname], "next_params": [param_string]}
        except ConfigurationError:
            PageClass = Page.by_name("/not-found")
        page = PageClass.from_params(params)
        return page.render()

    def make_callback(PageClass, page_name, method_name, method, callback_store_names):
        """
        Create a Dash callback from a Page callback.
        """
        outputs, inputs, states = method.callback_parameters
        logger.debug(
            "Page '%s' registered callback '%s' (%s, %s) -> %s",
            page_name,
            method_name,
            inputs,
            states,
            outputs,
        )

        def callback(*args):
            args, store = args[:-1], args[-1]
            page = PageClass.from_store(store)
            result = getattr(page, method_name)(*args)
            new_store = page.dump_store()
            logger.debug(
                "Page '%s' received callback '%s': %s, %s -> %s, %s",
                page_name,
                method_name,
                args,
                store,
                result,
                new_store,
            )
            if not isinstance(result, tuple):
                return (result, new_store)
            return result + (new_store,)

        callback_store_name = PageClass._store_name + f"-callback-{method_name}"
        callback_store_names.append(callback_store_name)
        outputs.append(Output(callback_store_name, "data"))
        states.append(State(PageClass._store_name, "data"))
        dash.callback(outputs, inputs, states)(callback)

    def store_callback(*args):
        """
        Update the Page store from the latest Page callback store.
        """
        half = len(args) // 2
        timestamps, datas = args[:half], args[half:]
        latest_index = max(range(len(datas)), key=lambda i: timestamps[i] or -1)
        latest = datas[latest_index]
        return latest

    # Now we loop through all registered pages and register their callbacks
    # with the dashboard application.
    for page_name in Page.list_available():
        PageClass = Page.by_name(page_name)
        PageClass._store_name = f"page-{page_name}-store"
        callback_store_names: List[str] = []
        for method_name, method in filter(
            lambda x: callable(x[1]), inspect.getmembers(PageClass)
        ):
            if not getattr(method, "is_callback", False):
                continue
            # We need to do this by calling the function we made `make_callback` instead
            # of doing all the work here in the loop so we don't run into a "late binding"
            # issue. See https://stackoverflow.com/questions/3431676/creating-functions-in-a-loop
            # for example.
            make_callback(
                PageClass, page_name, method_name, method, callback_store_names
            )
        PageClass._callback_stores = callback_store_names
        if callback_store_names:
            dash.callback(
                Output(PageClass._store_name, "data"),
                [Input(s, "modified_timestamp") for s in callback_store_names],
                [State(s, "data") for s in callback_store_names],
            )(store_callback)

    return dash


def create_app(config: Config, gunicorn: bool = True):
    app = Flask(__name__, instance_path=config.server.instance_path)
    app.config.from_object(config.server)

    loglevel = getattr(logging, config.project.loglevel.upper())
    app.logger.setLevel(loglevel)

    db.init_app(app)

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
    config = Config.from_toml(Path("./example-project"))
    app = create_app(config, gunicorn=False)
    app.run(debug=True)
