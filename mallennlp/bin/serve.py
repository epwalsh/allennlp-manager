import os

import click

from mallennlp.bin.common import requires_config, run_subprocess


@click.command()
@click.option("--update", is_flag=True, help="Pull the latest image before serving.")
@requires_config
def serve(config, update):
    """
    Serve the dashboard locally.
    """
    if update:
        click.secho(f"Updating {config.server.image}", fg="green")
        returncode = run_subprocess(f"docker pull {config.server.image}")
        if returncode != 0:
            raise click.ClickException(click.style("failed to update image", fg="red"))
    click.secho(f"Serving AllenNLP Manager for {config.project.name}", fg="green")
    returncode = run_subprocess(
        f"docker run "
        f"--rm "
        f"-p 5000:{config.server.port} "
        f"--mount type=bind,source={os.getcwd()},target=/opt/python/app/project "
        f"--env SERVER_CONCURRENCY={config.server.concurrency} "
        f"--memory={config.server.memory}m "
        f"--cpus={config.server.cpus} "
        f"{config.server.image}"
    )
    if returncode != 0:
        raise click.ClickException(click.style("server error", fg="red"))
