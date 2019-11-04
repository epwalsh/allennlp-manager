import os
import shlex
import subprocess

import click

from mallennlp.bin.common import requires_config


@click.command()
@requires_config
def serve(config):
    """
    Serve the dashboard locally.
    """
    args = shlex.split(
        f"docker run "
        f"--rm "
        f"-p 5000:{config.server.port} "
        f"--mount type=bind,source={os.getcwd()},target=/opt/python/app/project "
        f"{config.server.image}"
    )
    click.secho(f"Serving AllenNLP Manager for {config.project.name}", fg="green")
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output = process.stdout.readline()
        if process.poll() is not None and output == b"":
            break
        if output:
            click.echo(output.strip())
    if process.returncode != 0:
        raise click.ClickException(click.style("server error", fg="red"))
