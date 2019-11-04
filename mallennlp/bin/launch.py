import click

from mallennlp.bin.common import requires_config


@click.command()
@requires_config
def launch(config):
    """
    Launch the dashboard in your default browser.
    """
    url = f"http://localhost:{config.server.port}"
    click.launch(url)
