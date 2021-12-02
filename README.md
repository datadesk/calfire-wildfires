calfire-wildfires
=================

Download wildfires data from CalFire

Installation
------------

    $ pipenv install calfire-wildfires

Command-line usage
------------------

    Usage: calfirewildfires [OPTIONS] COMMAND [ARGS]...

      A command-line interface for downloading wildfires data from CalFire.

      Returns GeoJSON.

    Options:
      --help  Show this message and exit.

    Commands:
      active-fires    The latest active fires
      all-fires       Fires year-to-date, both active and contained

Download fires year-to-date, both active and contained :

    $ calfirewildfires all-fires

Download the latest active fires :

    $ calfirewildfires active-fires

Python usage
------------

Import the library. :

    >>> import calfire_wildfires

Download the fires year-to-date, both active and contained :

    >>> data = calfire_wildfires.get_all_fires()

Download the latest active fires :

    >>> data = calfire_wildfires.get_active_fires()

Contributing
------------

Install dependencies for development :

    $ pipenv install --dev

Run tests :

    $ make test

Ship new version to PyPI :

    $ make ship

Developing the CLI
------------------

The command-line interface is implemented using Click and setuptools. To
install it locally for development inside your virtual environment, run
the following installation command, as [prescribed by the Click
documentation](https://click.palletsprojects.com/en/7.x/setuptools/#setuptools-integration).
:

    $ pip install --editable .
