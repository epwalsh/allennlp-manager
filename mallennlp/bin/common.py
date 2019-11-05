from functools import wraps
import shlex
import subprocess

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
