import os

import click

from mallennlp.version import VERSION
from mallennlp.bin.serve import serve
from mallennlp.bin.new import new, init
from mallennlp.bin.edit import edit
from mallennlp.bin.launch import launch
from mallennlp.bin.user import user


@click.group()
@click.option(
    "--wd",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Set the working directory.",
)
@click.version_option(version=VERSION)
def main(wd):
    """
    AllenNLP Manager
    """
    if wd is not None:
        os.chdir(wd)


main.add_command(serve)
main.add_command(new)
main.add_command(init)
main.add_command(edit)
main.add_command(launch)
main.add_command(user)


if __name__ == "__main__":
    main()
