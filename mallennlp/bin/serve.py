import click

from mallennlp.bin.common import requires_config


@click.command()
@requires_config
def serve(config):
    click.secho(f"Serving AllenNLP Manager for {config.project.name}", fg="green")
