import click


@click.command()
@click.argument("name")
def new(name: str):
    click.secho(f"Creating project named {name}", fg="green")
