import os
from subprocess import check_output

import click

from mallennlp.bin.common import requires_config


@click.command()
@requires_config
def stop(config):
    """
    Stop the dashboard server.
    """
    wd = os.getcwd()
    container_id = check_output(
        f"docker ps "
        f"-a "
        f"-q "
        f"--filter ancestor={config.server.image} "
        f"--filter volume={wd} "
        "--format='{{.ID}}'",
        shell=True,
        universal_newlines=True,
    ).strip()
    if not container_id:
        click.secho("No running server detected", fg="yellow")
    else:
        click.echo(
            f"Found server running with container ID {click.style(container_id, fg='green')}"
        )
        check_output(f"docker stop {container_id}", shell=True, universal_newlines=True)
        click.secho("Server stopped", fg="yellow")
