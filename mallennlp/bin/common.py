from functools import wraps

import click

from mallennlp.config import Config
from mallennlp.exceptions import NotInProjectError


def requires_config(command):
    @wraps(command)
    def wrapped_command(*args, **kwargs):
        try:
            config = Config.from_toml()
        except NotInProjectError as exc:
            raise click.ClickException(click.style(str(exc), fg="red"))
        return command(config, *args, **kwargs)

    return wrapped_command
