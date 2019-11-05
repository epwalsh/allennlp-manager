import inspect
import logging
from pathlib import Path
import urllib.parse as urlparse

from allennlp.common.util import import_submodules
from dash import Dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask, redirect
from flask_login import LoginManager, login_required, logout_user

from mallennlp.config import Config
from mallennlp.dashboard.page import Page
from mallennlp.domain.user import User, AnonymousUser


def create_app(config: Config, gunicorn: bool = True):
    app = Flask(__name__)
    app.secret_key = config.server.secret

    loglevel = getattr(logging, config.project.loglevel.upper())
    if gunicorn:
        app.logger.handlers.clear()
        gunicorn_logger = logging.getLogger("gunicorn.error")
        gunicorn_logger.setLevel(loglevel)
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(loglevel)
    else:
        app.logger.setLevel(loglevel)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "/login"
    login_manager.anonymous_user = AnonymousUser
    login_manager.session_protection = "strong"

    @login_manager.user_loader
    def load_user(userid: str):
        return User.get(userid)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect("/login")

    return app


def create_dash(flask_app: Flask, config: Config):
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
                color="#72C0B9",
                dark=True,
            ),
            dbc.Container(id="page-content"),
        ]
    )

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
        return Page.by_name(pathname).from_params(params).render()

    # Import all dashboard pages so that they get registered.
    import_submodules("mallennlp.dashboard")

    def make_callback(method_name, method):
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
            logger.debug(
                "Page '%s' received callback '%s': %s, %s -> %s",
                page_name,
                method_name,
                args,
                store,
                result,
            )
            if not isinstance(result, tuple):
                result = (result,)
            return result

        states.append(State(PageClass.store_name, "data"))
        dash.callback(outputs, inputs, states)(callback)

    # Now we loop through all registered pages and register their callbacks
    # with the dashboard application.
    for page_name in Page.list_available():
        PageClass = Page.by_name(page_name)
        PageClass.store_name = f"page-{page_name}-store"
        for method_name, method in filter(
            lambda x: callable(x[1]), inspect.getmembers(PageClass)
        ):
            if not getattr(method, "is_callback", False):
                continue
            make_callback(method_name, method)

    return dash


if __name__ == "__main__":
    config = Config.from_toml(Path("./example-project"))
    app = create_app(config, gunicorn=False)
    dash = create_dash(app, config)
    app.run(debug=True)
