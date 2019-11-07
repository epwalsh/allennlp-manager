import click

from mallennlp.bin.common import requires_config, run_subprocess


@click.command()
@requires_config
def serve(config):
    """
    Serve the dashboard locally.
    """
    full_command = (
        "gunicorn "
        "--timeout 300 "
        "--worker-class gevent "
        f"--worker-connections {config.server.concurrency} "
        f"--bind :{config.server.port} "
        "mallennlp.wsgi:application"
    )
    returncode = run_subprocess(full_command)
    if returncode != 0:
        raise click.ClickException(click.style("failed to start server", fg="red"))
