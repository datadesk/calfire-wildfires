import click
from calfire_wildfires import get_fires, get_active_fires, get_inactive_fires


@click.group()
def cmd():
    """
    A command-line interface for downloading wildfires data from CalFire.

    Returns GeoJSON.
    """
    pass


@cmd.command(help="The latest fires, both active and contained")
def fires():
    click.echo(get_fires())


@cmd.command(help="The latest active fires")
def active_fires():
    click.echo(get_active_fires())


@cmd.command(help="The latest inactive fires")
def inactive_fires():
    click.echo(get_inactive_fires())


if __name__ == '__main__':
    cmd()
