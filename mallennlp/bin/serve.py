import os
from subprocess import check_output

import click

from mallennlp.bin.common import requires_config, run_subprocess


@click.command()
@click.option("--update", is_flag=True, help="Pull the latest image before serving.")
@click.option("-d", "--detach", is_flag=True, help="Run in background.")
@requires_config
def serve(config, update, detach):
    """
    Serve the dashboard locally.
    """
    if update:
        click.secho(f"Updating {config.server.image}", fg="green")
        returncode = run_subprocess(f"docker pull {config.server.image}")
        if returncode != 0:
            raise click.ClickException(click.style("failed to update image", fg="red"))
    click.echo(
        f"Serving AllenNLP Manager for {click.style(config.project.name, fg='green', bold=True)}"
    )
    if detach:
        command_prefix = "docker run -d"
    else:
        command_prefix = "docker run"
    full_command = (
        f"{command_prefix} "
        f"--rm "
        f"-p 5000:{config.server.port} "
        f"--mount type=bind,source={os.getcwd()},target=/opt/python/app/project "
        f"--env SERVER_CONCURRENCY={config.server.concurrency} "
        f"--memory={config.server.memory}m "
        f"--cpus={config.server.cpus} "
        f"{config.server.image}"
    )
    if detach:
        container_id = check_output(
            full_command, shell=True, universal_newlines=True
        ).strip()
        if not container_id:
            raise click.ClickException(click.style("failed to start server", fg="red"))
        click.echo(
            f"Started server with container ID {click.style(container_id[0:12], fg='green')}"
        )
    else:
        returncode = run_subprocess(full_command)
        if returncode != 0:
            raise click.ClickException(click.style("failed to start server", fg="red"))
