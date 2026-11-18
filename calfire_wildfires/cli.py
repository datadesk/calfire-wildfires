"""The calfirewildfires command-line interface."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import click

from calfire_wildfires import CalFireError, get_active_fires, get_all_fires
from calfire_wildfires.fetch import DEFAULT_TIMEOUT


def _common_options(func: Callable[..., Any]) -> Callable[..., Any]:
    """Add the options every download command shares.

    Args:
        func: The click command function to decorate.

    Returns:
        The same function with the indent, timeout and verbose options attached.
    """
    decorators = [
        click.option("--indent", default=0, help="Indentation of output"),
        click.option(
            "--timeout",
            default=DEFAULT_TIMEOUT,
            show_default=True,
            type=click.FloatRange(min=1),
            help="Seconds to wait for CAL FIRE on each try",
        ),
        click.option("--verbose", is_flag=True, help="Print each request to stderr"),
    ]
    for decorator in reversed(decorators):
        func = decorator(func)
    return func


def _download(
    getter: Callable[..., dict],
    indent: int,
    timeout: float,
    verbose: bool,
) -> None:
    """Download a list and print it as JSON.

    Args:
        getter: ``get_active_fires`` or ``get_all_fires``.
        indent: How many spaces to indent the output. Zero prints one line.
        timeout: Seconds to wait for CAL FIRE on each try.
        verbose: Whether to print each request to standard error.

    Raises:
        click.ClickException: If CAL FIRE cannot be reached or sends back an
            error, so the command prints one line starting with "Error:" and
            exits with code 1.
    """
    try:
        data = getter(verbose=verbose, timeout=timeout)
    except CalFireError as error:
        raise click.ClickException(str(error)) from error
    click.echo(json.dumps(data, indent=indent or None))


@click.group()
def cmd() -> None:
    """A command-line interface for downloading wildfires data from CalFire.

    Returns GeoJSON.
    """
    pass


@cmd.command(help="The latest active fires JSON")
@_common_options
def active_fires(indent, timeout, verbose):
    _download(get_active_fires, indent, timeout, verbose)


@cmd.command(help="All active and inactive fires year to date JSON")
@_common_options
def all_fires(indent, timeout, verbose):
    _download(get_all_fires, indent, timeout, verbose)


if __name__ == "__main__":
    cmd()
