import click
from calfire_wildfires import get_active_fires, get_all_fires


@click.group()
def cmd():
    """
    A command-line interface for downloading wildfires data from CalFire.

    Returns GeoJSON.
    """
    pass


@cmd.command(help="The latest active fires JSON")
def active_fires():
    click.echo(get_active_fires())


@cmd.command(help="The latest active fires JSON")
def all_fires():
    click.echo(get_all_fires())


if __name__ == '__main__':
    cmd()
