import click

from mallennlp.bin.common import requires_config, validate_password


@click.group("user")
@click.pass_context
@requires_config
def user_group(config, ctx):
    """
    Manage dashboard users.
    """
    from mallennlp.services.db import get_db_from_cli
    from mallennlp.services.user import UserService

    db = get_db_from_cli(config)
    user_service = UserService(db=db)
    ctx.obj = user_service


def validate_username(ctx, param, value):
    user_service = ctx.obj
    if user_service.find(value, check_password=False) is None:
        raise click.BadParameter(
            click.style(f"Unknown username {click.style(value, bold=True)}", fg="red")
        )
    return value


@click.command("changepw")
@click.argument("username", callback=validate_username)
@click.option(
    "--password",
    prompt="Set dashboard password",
    hide_input=True,
    confirmation_prompt=True,
    callback=validate_password,
)
@click.pass_obj
def changepw(user_service, username, password):
    """
    Change dashboard user's password.
    """
    success = user_service.changepw(username, password)
    if not success:
        raise click.ClickException(click.style("failed to change password", fg="red"))
    click.secho("Password successfully changed", fg="green")


user_group.add_command(changepw)
