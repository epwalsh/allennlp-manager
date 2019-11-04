import click

from mallennlp.bin.common import requires_config


@click.command()
@requires_config
def launch(config):
    url = f"http://localhost:{config.server.port}"
    click.launch(url)
