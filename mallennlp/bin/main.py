import os

import click

from mallennlp.bin.serve import serve
from mallennlp.bin.new import new
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
def main(wd):
    """
    AllenNLP Manager
    """
    if wd is not None:
        os.chdir(wd)


main.add_command(serve)
main.add_command(new)
main.add_command(edit)
main.add_command(launch)
main.add_command(user)
main.add_command(stop)


if __name__ == "__main__":
    main()
