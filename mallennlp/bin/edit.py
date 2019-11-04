import click

from mallennlp.bin.common import requires_config


@click.command()
@requires_config
def edit(config):
    click.launch(config.CONFIG_PATH)
