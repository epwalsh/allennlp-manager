import click

from mallennlp.bin.serve import serve
from mallennlp.bin.new import new
from mallennlp.bin.edit import edit
from mallennlp.bin.launch import launch


@click.group()
def main():
    pass


main.add_command(serve)
main.add_command(new)
main.add_command(edit)
main.add_command(launch)


if __name__ == "__main__":
    main()
