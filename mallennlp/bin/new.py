import os
from pathlib import Path

import click

from mallennlp.config import Config, ProjectConfig, ServerConfig
from mallennlp.services.db import init_db


@click.command()
@click.argument("name")
@click.option("--display-name", type=str)
@click.option("--loglevel", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]))
@click.option("--server-image", type=str)
@click.option("--server-port", type=int)
@click.option("--server-secret", type=str)
@click.option("--server-concurrency", type=int)
@click.option("--server-memory", type=int)
@click.option("--server-cpus", type=float)
def new(name: str, **kwargs):
    """
    Initialize a new project directory.
    """
    os.mkdir(name)
    project_options = {
        k: v for k, v in kwargs.items() if not k.startswith("server_") and v is not None
    }
    server_options = {
        k[7:]: v for k, v in kwargs.items() if k.startswith("server_") and v is not None
    }
    path = Path(name).resolve()
    config = Config(
        ProjectConfig(path, name=name, **project_options),
        ServerConfig(path, **server_options),
    )
    os.makedirs(config.server.instance_path)
    config.to_toml(path)
    init_db(config)
    click.secho(f"Created project named {name}", fg="green")
    click.echo(
        "To edit the project's config, run 'mallennlp edit' from within the project "
        "directory or edit the 'Project.toml' file directly."
    )
