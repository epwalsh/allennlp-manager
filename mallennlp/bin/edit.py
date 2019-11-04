import click

from mallennlp.bin.common import requires_config


@click.command()
@requires_config
def edit(config):
    """
    Edit the project's configuration file.
    """
    click.launch(config.CONFIG_PATH)
