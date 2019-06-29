calfire-wildfires
=================

Download wildfires data from CalFire

Installation
------------

::

    $ pipenv install calfire-wildfires


Command-line usage
------------------

::

    Usage: calfirewildfires [OPTIONS] COMMAND [ARGS]...

      A command-line interface for downloading wildfires data from CalFire.

      Returns GeoJSON.

    Options:
      --help  Show this message and exit.

    Commands:
      active-fires    The latest active fires
      fires           The latest fires, both active and contained
      inactive-fires  The latest inactive fires

Download the latest fires, both active and contained ::

    $ calfirewildfires fires

Download the latest active fires ::

    $ calfirewildfires active-fires

Download the latest inactive fires ::

    $ calfirewildfires inactive-fires


Python usage
------------

Import the library. ::

    >>> import calfire_wildfires

Download the latest fires, both active and contained ::

    >>> data = calfire_wildfires.get_fires()

Download the latest active fires ::

    >>> data = calfire_wildfires.get_active_fires()

Download the latest inactive fires ::

    >>> data = calfire_wildfires.get_inactive_fires()


Contributing
------------

Install dependencies for development ::

    $ pipenv install --dev

Run tests ::

    $ make test

Ship new version to PyPI ::

    $ make ship


Developing the CLI
------------------

The command-line interface is implemented using Click and setuptools. To install it locally for development inside your virtual environment, run the following installation command, as `prescribed by the Click documentation <https://click.palletsprojects.com/en/7.x/setuptools/#setuptools-integration>`_. ::

    $ pip install --editable .
