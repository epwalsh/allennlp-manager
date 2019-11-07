import os
from pathlib import Path

import click

from mallennlp.bin.common import validate_password
from mallennlp.domain.config import ProjectConfig, ServerConfig
from mallennlp.services.db import init_db, get_db_from_cli
from mallennlp.services.config import Config
from mallennlp.services.user import UserService


def init_project(
    verb: str, name: str, path: Path, username: str, password: str, **kwargs
):
    if (path / Config.CONFIG_PATH).exists():
        raise click.ClickException(click.style("project already exists", fg="red"))

    # Initialize config.
    project_options = {
        k: v for k, v in kwargs.items() if not k.startswith("server_") and v is not None
    }
    server_options = {
        k[7:]: v for k, v in kwargs.items() if k.startswith("server_") and v is not None
    }
    config = Config(
        ProjectConfig(path, name=name, **project_options),
        ServerConfig(path, **server_options),
    )

    # Ensure the server's instance path exists.
    os.makedirs(config.server.instance_path)

    # Initialize the database file.
    init_db(config)

    # Add the user to the database.
    db = get_db_from_cli(config)
    user_service = UserService(db=db)
    user_service.create(username, password)

    # Save the config to the 'Project.toml' file in the project directory.
    config.to_toml(path)

    click.echo(f"{verb} project named {click.style(name, fg='green', bold=True)}")
    click.echo(
        f" --> To edit the project's config, run {click.style('mallennlp edit', fg='yellow')} "
        f"from within the project "
        f"directory or edit the {click.style('Project.toml', fg='green')} file directly."
    )
    click.echo(
        f" --> To serve the dashboard, run {click.style('mallennlp serve', fg='yellow')} "
        f"from within the project directory."
    )
    click.echo(
        f" --> You can log in to the dashboard with the username {click.style(username, bold=True, fg='green')}"
    )


def validate_name(ctx, param, value):
    if os.path.exists(value):
        raise click.ClickException(
            click.style("directory already exists, try ", fg="red")
            + click.style("mallennlp init", fg="yellow")
            + click.style(" instead", fg="red")
        )
    return value


@click.command()
@click.argument("name", callback=validate_name)
@click.option(
    "--username",
    prompt="Set dashboard username",
    default=lambda: os.environ.get("USER", "admin"),
)
@click.option(
    "--password",
    prompt="Set dashboard password",
    hide_input=True,
    confirmation_prompt=True,
    callback=validate_password,
)
@click.option("--display-name", type=str)
@click.option("--loglevel", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]))
@click.option("--server-image", type=str)
@click.option("--server-port", type=int)
@click.option("--server-secret", type=str)
@click.option("--server-concurrency", type=int)
@click.option("--server-memory", type=int)
@click.option("--server-cpus", type=float)
@click.option("--server-imports", type=str, multiple=True)
def new(name: str, username: str, password: str, **kwargs):
    """
    Create a new project directory.
    """
    os.mkdir(name)
    path = Path(name).resolve()
    name = path.name
    init_project("Created", name, path, username, password, **kwargs)


@click.command()
@click.option(
    "--username",
    prompt="Set dashboard username",
    default=lambda: os.environ.get("USER", "admin"),
)
@click.option(
    "--password",
    prompt="Set dashboard password",
    hide_input=True,
    confirmation_prompt=True,
    callback=validate_password,
)
@click.option("--display-name", type=str)
@click.option("--loglevel", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]))
@click.option("--server-image", type=str)
@click.option("--server-port", type=int)
@click.option("--server-secret", type=str)
@click.option("--server-concurrency", type=int)
@click.option("--server-memory", type=int)
@click.option("--server-cpus", type=float)
@click.option("--server-imports", type=str, multiple=True)
def init(username: str, password: str, **kwargs):
    """
    Initialize a project in existing directory.
    """
    path = Path("./").resolve()
    name = path.name
    init_project("Initialized", name, path, username, password, **kwargs)
