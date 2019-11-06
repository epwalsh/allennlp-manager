import pkg_resources
import sqlite3

from flask import current_app, g

from mallennlp.domain.config import Config


def get_db_from_cli(config: Config):
    db = sqlite3.connect(config.server.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    return db


def get_db_from_app():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db_from_app(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(config: Config):
    db = get_db_from_cli(config)
    schema_path = pkg_resources.resource_filename("mallennlp", "services/schema.sql")
    with open(schema_path, "rb") as schema_file:
        db.executescript(schema_file.read().decode("utf-8"))


def init_app(app):
    app.teardown_appcontext(close_db_from_app)
