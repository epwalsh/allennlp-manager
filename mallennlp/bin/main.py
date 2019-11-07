import os
import sys

import click

from mallennlp.version import VERSION
from mallennlp.bin.serve import serve
from mallennlp.bin.new import new, init
from mallennlp.bin.edit import edit
from mallennlp.bin.launch import launch
from mallennlp.bin.user import user
from mallennlp.bin.stop import stop


@click.group()
@click.option(
    "--wd",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Set the working directory.",
)
@click.version_option(version=VERSION)
def main(wd, version):
    """
    AllenNLP Manager
    """
    if version:
        click.echo(f"AllenNLP Manager v{VERSION}")
        sys.exit(0)
    if wd is not None:
        os.chdir(wd)


main.add_command(serve)
main.add_command(new)
main.add_command(init)
main.add_command(edit)
main.add_command(launch)
main.add_command(user)
main.add_command(stop)


if __name__ == "__main__":
    main()
