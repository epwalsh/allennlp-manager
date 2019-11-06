from functools import wraps
import shlex
import subprocess

import click

from mallennlp.domain.config import Config
from mallennlp.exceptions import NotInProjectError
from mallennlp.services.user import UserService


def requires_config(command):
    @wraps(command)
    def wrapped_command(*args, **kwargs):
        try:
            config = Config.from_toml()
        except NotInProjectError as exc:
            raise click.ClickException(click.style(str(exc), fg="red"))
        return command(config, *args, **kwargs)

    return wrapped_command


def run_subprocess(command: str) -> int:
    args = shlex.split(command)
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output = process.stdout.readline()
        if process.poll() is not None and output == b"":
            break
        if output:
            click.echo(output.strip())
    return process.returncode


def validate_password(ctx, param, value):
    ok, reason = UserService.validate_password(value)
    if not ok:
        raise click.BadParameter(click.style(reason, fg="red"))
    return value
