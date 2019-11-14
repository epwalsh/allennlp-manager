import click

from mallennlp.bin.common import requires_config


@click.group("db")
@click.pass_context
@requires_config
def db_group(config, ctx):
    """
    Manage the backend database.
    """
    from mallennlp.services.db import get_db_from_cli

    db = get_db_from_cli(config)
    ctx.obj = db


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


def validate_table(ctx, param, value):
    from mallennlp.services.db import all_tables

    tables = list(all_tables())
    if value not in list(all_tables()):
        raise click.ClickException(
            click.style("Invalid table name. ", fg="red")
            + click.style(f"Choices are [{', '.join(tables)}]")
        )
    return value


@click.command("reset")
@click.argument("table", callback=validate_table)
@click.option(
    "--force",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to reset this database table?",
)
@click.pass_obj
def reset(db, table: str):
    click.echo(f"Resetting db table {click.style(table, fg='green')}...")

    from mallennlp.services.db import init_tables, Tables
    from mallennlp.services.experiment import ExperimentService

    init_tables(db, (table,))
    if table == Tables.EXPERIMENTS.value:
        # Recursively search project for experiments and populate database.
        entries = [s.get_db_fields() for s in ExperimentService.find_experiments()]
        if entries:
            click.echo(
                f"Found {click.style(str(len(entries)), fg='green')} experiments"
            )
            ExperimentService.init_db_table(db=db, entries=entries)
    db.close()
    click.secho("Success!", fg="green")


db_group.add_command(reset)
