import os
from pathlib import Path

import click

from mallennlp.config import Config, ProjectConfig, ServerConfig


@click.command()
@click.argument("name")
def new(name: str):
    os.mkdir(name)
    config = Config(ProjectConfig(name=name), ServerConfig())
    config.to_toml(Path(name))
    click.secho(f"Created project named {name}", fg="green")
    click.echo(
        "To edit the project's config, run 'mallennlp edit' from within the project "
        "directory or edit the 'Project.toml' file directly."
    )
