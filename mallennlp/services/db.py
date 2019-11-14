from enum import Enum
import pkg_resources
import sqlite3
from typing import Iterable

from flask import current_app, g

from mallennlp.services.config import Config


class Tables(Enum):
    USERS = "users"
    EXPERIMENTS = "experiments"


def _get_db(uri: str):
    db = sqlite3.connect(uri, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row

    # Custom function for matching rows that contain any of the tags in the function
    # args.
    def has_any_tags(row_tag_str: str, *tags: str):
        row_tags = row_tag_str.split(" ")
        return int(any(t in row_tags for t in tags))

    db.create_function("HasAnyTags", -1, has_any_tags)

    # Custom function for matching rows that contain all of the tags in the function
    # args.
    def has_all_tags(row_tag_str: str, *tags: str):
        row_tags = row_tag_str.split(" ")
        return int(all(t in row_tags for t in tags))

    db.create_function("HasAllTags", -1, has_all_tags)

    return db


def get_db_from_config(config: Config):
    return _get_db(config.server.DATABASE)


def get_db_from_cli(config: Config):
    return get_db_from_config(config)


def get_db_from_app():
    if "db" not in g:
        g.db = _get_db(current_app.config["DATABASE"])
    return g.db


def close_db_from_app(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def all_tables() -> Iterable[str]:
    for t in Tables:
        yield t.value


def init_db(config: Config, tables: Iterable[str] = None):
    if tables is None:
        tables = all_tables()
    db = get_db_from_config(config)
    init_tables(db, tables)


def init_tables(db, tables: Iterable[str] = None):
    if tables is None:
        tables = all_tables()
    for table in tables:
        schema_path = pkg_resources.resource_filename(
            "mallennlp", f"schema/{table}.sql"
        )
        with open(schema_path, "rb") as schema_file:
            db.executescript(schema_file.read().decode("utf-8"))


def init_app(app):
    app.teardown_appcontext(close_db_from_app)
