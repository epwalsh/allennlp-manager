import click

from mallennlp.bin.common import requires_config, validate_password


PERMISSIONS = ["READ", "READ_WRITE", "ADMIN"]


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


def validate_new_username(ctx, param, value):
    user_service = ctx.obj
    if user_service.find(value, check_password=False) is not None:
        raise click.BadParameter(
            click.style(
                f"Username {click.style(value, bold=True)} already exists", fg="red"
            )
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


@click.command("add")
@click.argument("username", callback=validate_new_username)
@click.option(
    "--password",
    prompt="Set dashboard password",
    hide_input=True,
    confirmation_prompt=True,
    callback=validate_password,
)
@click.option("--permissions", type=click.Choice(PERMISSIONS), default="READ")
@click.pass_obj
def add(user_service, username, password, permissions):
    """
    Add a new dashboard user.
    """
    from mallennlp.domain.user import Permissions

    permissions = getattr(Permissions, permissions)
    user_service.create(username, password, permissions=permissions)
    click.echo(
        f"User {click.style(username, bold=True, fg='green')} successfully created"
    )


@click.command("set-permissions")
@click.argument("username", callback=validate_username)
@click.argument("permissions", type=click.Choice(PERMISSIONS))
@click.pass_obj
def set_permissions(user_service, username, permissions):
    from mallennlp.domain.user import Permissions

    permissions = getattr(Permissions, permissions)
    user = user_service.set_permissions(username, permissions)
    if not user:
        raise click.ClickException(click.style("failed to set permissions", fg="red"))
    click.echo(
        f"User {click.style(username, bold=True, fg='green')} "
        f"permissions now {click.style(permissions.name, bold=True)}"
    )


user_group.add_command(changepw)
user_group.add_command(add)
user_group.add_command(set_permissions)
