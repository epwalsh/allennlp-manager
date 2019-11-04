import click

from mallennlp.bin.serve import serve
from mallennlp.bin.new import new


@click.group()
def main():
    pass


main.add_command(serve)
main.add_command(new)


if __name__ == "__main__":
    main()
